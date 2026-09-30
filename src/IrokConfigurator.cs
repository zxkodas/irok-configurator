// Irok Configurator - single-file launcher and installer for the Irok web driver
// (https://hid.irok.cn). Compiled with the in-box .NET Framework csc.exe, so it
// runs on any Windows 10/11 with no runtime install and no admin rights.
//
// Modes:
//   (none)        install (idempotent), then launch
//   --open        launch only
//   --uninstall   remove shortcuts, registry entry and files
//   --silent      suppress UI (for scripts and testing)
//   --help
//
// Deliberately C# 5 compatible: the in-box csc.exe is not Roslyn and rejects
// string interpolation, nameof, null-conditional and expression-bodied members.

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Reflection;
using System.Text;
using System.Windows.Forms;
using System.Management;
using Microsoft.Win32;

namespace IrokConfigurator
{
    internal static class Program
    {
        private const string AppName = "Irok Configurator";
        private const string AppId = "IrokConfigurator";
        private const string ExeFile = "IrokConfigurator.exe";
        internal const string DefaultUrl = "https://hid.irok.cn";
        private const string Version = "1.0.0";
        private const string UninstKey = @"Software\Microsoft\Windows\CurrentVersion\Uninstall\" + AppId;
        private const string EmbeddedIcon = "irok.ico";

        private static bool silent = false;

        private static string InstallDir
        {
            get
            {
                return Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                    "Programs", AppId);
            }
        }

        private static string ProfileDir { get { return Path.Combine(InstallDir, "profile"); } }
        private static string IconPath { get { return Path.Combine(InstallDir, EmbeddedIcon); } }
        private static string ConfigPath { get { return Path.Combine(InstallDir, "config.txt"); } }
        private static string LogPath { get { return Path.Combine(InstallDir, "IrokConfigurator.log"); } }
        private static string ExePath { get { return Path.Combine(InstallDir, ExeFile); } }

        private static string StartMenuLink
        {
            get
            {
                return Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                    @"Microsoft\Windows\Start Menu\Programs", AppName + ".lnk");
            }
        }

        private static string DesktopLink
        {
            get
            {
                return Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory),
                    AppName + ".lnk");
            }
        }

        private static int Main(string[] args)
        {
            string mode = "install";
            for (int i = 0; i < args.Length; i++)
            {
                string a = args[i].ToLowerInvariant();
                if (a == "--silent" || a == "/s") silent = true;
                else if (a == "--uninstall") mode = "uninstall";
                else if (a == "--open") mode = "open";
                else if (a == "--help" || a == "-h" || a == "/?") mode = "help";
            }

            try
            {
                if (mode == "help") { PrintHelp(); return 0; }
                if (mode == "uninstall") return Uninstall();
                if (mode == "open") return Open();
                return InstallAndOpen();
            }
            catch (Exception ex)
            {
                Log("FATAL " + ex);
                Info("Irok Configurator could not finish.\n\n" + ex.Message, true);
                return 1;
            }
        }

        // ---------- install ----------

        private static int InstallAndOpen()
        {
            Config cfg = Install();
            if (cfg == null) return 1;
            return Launch(cfg);
        }

        private static Config Install()
        {
            Directory.CreateDirectory(InstallDir);
            Log("install -> " + InstallDir);

            // 1. place a copy of ourselves in the install dir, so the shortcut
            //    survives the user moving or deleting the original download
            string self = Assembly.GetExecutingAssembly().Location;
            if (!PathsEqual(self, ExePath))
            {
                try
                {
                    File.Copy(self, ExePath, true);
                    Log("copied self to " + ExePath);
                }
                catch (Exception ex)
                {
                    // if it fails we can still run from where we are
                    Log("self-copy failed (continuing): " + ex.Message);
                }
            }

            // 2. icon: embedded copy as the baseline, web copy as a refresh
            WriteEmbeddedIcon();
            TryFetchIcon();

            // 3. config
            bool configExisted = File.Exists(ConfigPath);
            Config cfg = Config.Load(ConfigPath);
            if (!configExisted) { cfg.Save(ConfigPath); Log("wrote default config"); }

            // 4. seed the isolated profile so Chrome skips its first-run screen.
            //    Never clobber an existing profile - the user's grant lives there.
            SeedProfile();

            // 5. shortcuts
            CreateShortcut(StartMenuLink);
            if (cfg.DesktopShortcut) CreateShortcut(DesktopLink);
            else TryDelete(DesktopLink);

            // 6. Add or Remove Programs
            RegisterUninstall();

            if (!silent)
            {
                Info(AppName + " installed.\n\n" +
                     "Press the Windows key, type \"Irok\", press Enter.\n\n" +
                     "The first time you open it, dismiss Chrome's welcome screen " +
                     "and pick your keyboard when asked. Chrome remembers that " +
                     "choice, so it is a one-time step.", false);
            }
            return cfg;
        }

        private static void WriteEmbeddedIcon()
        {
            try
            {
                if (File.Exists(IconPath)) return;
                Stream s = Assembly.GetExecutingAssembly().GetManifestResourceStream(EmbeddedIcon);
                if (s == null) { Log("no embedded icon resource"); return; }
                using (s)
                using (FileStream f = File.Create(IconPath))
                {
                    byte[] buf = new byte[8192];
                    int n;
                    while ((n = s.Read(buf, 0, buf.Length)) > 0) f.Write(buf, 0, n);
                }
                Log("extracted embedded icon");
            }
            catch (Exception ex) { Log("icon extract failed: " + ex.Message); }
        }

        private static void TryFetchIcon()
        {
            // Best effort only. A failure just means we keep the embedded icon.
            try
            {
                ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12;
                string tmp = IconPath + ".tmp";
                WebClient wc = new WebClient();
                wc.DownloadFile(Config.Load(ConfigPath).Url.TrimEnd('/') + "/favicon.ico", tmp);

                byte[] b = File.ReadAllBytes(tmp);
                bool validIco = b.Length > 22 && b[0] == 0x00 && b[1] == 0x00 &&
                                 b[2] == 0x01 && b[3] == 0x00;
                if (validIco) { File.Copy(tmp, IconPath, true); Log("refreshed icon from web"); }
                else Log("fetched icon was not a valid ICO, keeping embedded one");
                File.Delete(tmp);
            }
            catch (Exception ex) { Log("icon fetch skipped: " + ex.Message); }
        }

        private static void SeedProfile()
        {
            try
            {
                string def = Path.Combine(ProfileDir, "Default");
                Directory.CreateDirectory(def);
                string prefs = Path.Combine(def, "Preferences");
                if (File.Exists(prefs)) return; // don't clobber a real profile
                string json = "{\"profile\":{\"exit_type\":\"Normal\",\"exited_cleanly\":true}}";
                File.WriteAllText(prefs, json);
                Log("seeded profile prefs");
            }
            catch (Exception ex) { Log("profile seed failed (harmless): " + ex.Message); }
        }

        // ---------- launch ----------

        private static int Open()
        {
            Config cfg = Config.Load(ConfigPath);
            return Launch(cfg);
        }

        private static int Launch(Config cfg)
        {
            string browser = ResolveBrowser(cfg);
            if (browser == null)
            {
                Log("no chromium browser found");
                Info("No supported browser was found.\n\n" +
                     "Irok Configurator needs a Chromium-based browser " +
                     "(Edge, Chrome, Brave, Opera or Vivaldi) because the Irok web " +
                     "driver uses the WebHID API, which Firefox and Safari do not " +
                     "implement.\n\n" +
                     "Install Microsoft Edge (it ships with Windows) and run this " +
                     "again.", true);
                return 2;
            }

            StringBuilder args = new StringBuilder();
            args.Append("--app=").Append(cfg.Url);
            if (!cfg.SharedProfile)
            {
                args.Append(" --user-data-dir=\"").Append(ProfileDir).Append('"');
            }
            // Throwaway profile, so suppress everything that would phone home or
            // nag: GCM registration, sync, component updates, default-browser
            // prompts. None of this affects WebHID.
            args.Append(" --no-first-run");
            args.Append(" --no-default-browser-check");
            args.Append(" --no-service-autorun");
            args.Append(" --disable-background-networking");
            args.Append(" --disable-sync");
            args.Append(" --disable-component-update");
            args.Append(" --disable-default-apps");
            // Keeps the app window from sitting in the taskbar's Chrome group
            // when the user opts into a shared profile.
            args.Append(" --class=").Append(AppId);

            Log("launch: " + browser + " " + args);
            try
            {
                ProcessStartInfo psi = new ProcessStartInfo(browser, args.ToString());
                // Shell launch on purpose: UseShellExecute=false would make the
                // browser inherit our stdio handles, so its stderr would spew into
                // whatever console launched us and our caller would block until
                // the browser exited.
                psi.UseShellExecute = true;
                Process.Start(psi);
                return 0;
            }
            catch (Exception ex)
            {
                Log("launch failed: " + ex.Message);
                Info("Could not start the browser.\n\n" + ex.Message +
                     "\n\nIf the path is wrong, edit:\n" + ConfigPath, true);
                return 3;
            }
        }

        private static string ResolveBrowser(Config cfg)
        {
            // 1. explicit path wins, so a user can point at a portable install
            if (cfg.BrowserPath.Trim().Length > 0)
            {
                if (File.Exists(cfg.BrowserPath.Trim())) return cfg.BrowserPath.Trim();
                Log("BrowserPath does not exist: " + cfg.BrowserPath);
            }

            // 2. otherwise take the first candidate that exists, in preference order
            List<string> order = new List<string>();
            string[] all = { "edge", "chrome", "brave", "opera", "vivaldi" };
            if (cfg.Preferred.Trim().Length > 0)
            {
                order.Add(cfg.Preferred.Trim().ToLowerInvariant());
                foreach (string b in all) if (b != order[0]) order.Add(b);
            }
            else
            {
                foreach (string b in all) order.Add(b);
            }

            foreach (string key in order)
            {
                foreach (string cand in BrowserCandidates(key))
                {
                    if (File.Exists(cand)) { Log("browser: " + key + " -> " + cand); return cand; }
                }
            }
            return null;
        }

        private static string[] Roots()
        {
            return new string[]
            {
                Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles),
                Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86),
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData)
            };
        }

        private static string[] BrowserCandidates(string key)
        {
            string[] r = Roots();
            switch (key)
            {
                case "edge":
                    return new string[]
                    {
                        Path.Combine(r[1], @"Microsoft\Edge\Application\msedge.exe"),
                        Path.Combine(r[0], @"Microsoft\Edge\Application\msedge.exe"),
                        Path.Combine(r[2], @"Microsoft\Edge\Application\msedge.exe")
                    };
                case "chrome":
                    return new string[]
                    {
                        Path.Combine(r[0], @"Google\Chrome\Application\chrome.exe"),
                        Path.Combine(r[1], @"Google\Chrome\Application\chrome.exe"),
                        Path.Combine(r[2], @"Google\Chrome\Application\chrome.exe")
                    };
                case "brave":
                    return new string[]
                    {
                        Path.Combine(r[0], @"BraveSoftware\Brave-Browser\Application\brave.exe"),
                        Path.Combine(r[1], @"BraveSoftware\Brave-Browser\Application\brave.exe"),
                        Path.Combine(r[2], @"BraveSoftware\Brave-Browser\Application\brave.exe")
                    };
                case "opera":
                    return new string[]
                    {
                        Path.Combine(r[0], @"Opera\opera.exe"),
                        Path.Combine(r[1], @"Opera\opera.exe"),
                        Path.Combine(r[2], @"Programs\Opera\opera.exe")
                    };
                case "vivaldi":
                    return new string[]
                    {
                        Path.Combine(r[2], @"Vivaldi\Application\vivaldi.exe"),
                        Path.Combine(r[0], @"Vivaldi\Application\vivaldi.exe")
                    };
                default:
                    return new string[0];
            }
        }

        // ---------- uninstall ----------

        private static int Uninstall()
        {
            Log("uninstall -> " + InstallDir);
            TryDelete(StartMenuLink);
            TryDelete(DesktopLink);

            try { Registry.CurrentUser.DeleteSubKeyTree(UninstKey, false); }
            catch (Exception ex) { Log("registry delete failed: " + ex.Message); }

            // The configurator window is a whole browser process tree holding our
            // profile open, so the rmdir below fails without this. Only processes
            // whose command line contains OUR profile path are matched, which never
            // includes the user's own browser windows. With SharedProfile=true
            // there is no such path in the command line, so we match nothing.
            int killed = KillProfileBrowsers();
            Log("closed " + killed + " configurator browser process(es)");

            if (!silent) Info(AppName + " removed.", false);

            if (Directory.Exists(InstallDir))
            {
                // Cannot delete a running exe, so hand the work to a detached cmd
                // that waits for this process to exit and retries while the
                // browser tree unwinds.
                ProcessStartInfo psi = new ProcessStartInfo("cmd.exe", UninstallCommand(InstallDir));
                psi.UseShellExecute = false;
                psi.CreateNoWindow = true;
                psi.WindowStyle = ProcessWindowStyle.Hidden;
                try { Process.Start(psi); }
                catch (Exception ex) { Log("self-delete failed: " + ex.Message); }

                // Last resort: ask Windows to remove it at next boot, which
                // ignores lock handles. Needs elevation; harmless if it fails.
                try
                {
                    if (ScheduleDeleteOnReboot(InstallDir)) Log("scheduled install dir for deletion at next reboot");
                }
                catch (Exception ex) { Log("reboot delete could not be scheduled: " + ex.Message); }
            }
            return 0;
        }

        private const int MOVEFILE_DELAY_UNTIL_REBOOT = 0x4;

        [System.Runtime.InteropServices.DllImport("kernel32.dll", CharSet = System.Runtime.InteropServices.CharSet.Unicode, SetLastError = true)]
        private static extern bool MoveFileEx(string existing, string newName, int flags);

        private static bool ScheduleDeleteOnReboot(string dir)
        {
            return MoveFileEx(dir, null, MOVEFILE_DELAY_UNTIL_REBOOT);
        }

        private static string UninstallCommand(string dir)
        {
            StringBuilder sb = new StringBuilder("/c ");
            // 30 attempts, ~2s apart: the browser tree can take a while to let go
            // of its profile handles. Each rmdir clears what it can, so partial
            // progress is kept across attempts.
            for (int i = 0; i < 30; i++)
            {
                sb.Append("ping -n 3 127.0.0.1 >nul & rmdir /s /q \"").Append(dir).Append("\" 2>nul & ");
            }
            return sb.ToString();
        }

        private static int KillProfileBrowsers()
        {
            int killed = 0;
            List<int> roots = new List<int>();
            List<int> all = new List<int>();

            try
            {
                string needle = ProfileDir;
                ManagementObjectSearcher searcher =
                    new ManagementObjectSearcher("SELECT ProcessId, Name, CommandLine FROM Win32_Process");
                foreach (ManagementObject mo in searcher.Get())
                {
                    try
                    {
                        string name = Convert.ToString(mo["Name"]);
                        if (name == null) continue;
                        name = name.ToLowerInvariant();
                        if (!name.EndsWith("chrome.exe") && !name.EndsWith("msedge.exe") &&
                            !name.EndsWith("brave.exe") && !name.EndsWith("opera.exe") &&
                            !name.EndsWith("vivaldi.exe") && !name.EndsWith("iexplore.exe"))
                        {
                            continue;
                        }
                        string cmd = Convert.ToString(mo["CommandLine"]);
                        if (cmd == null || cmd.IndexOf(needle, StringComparison.OrdinalIgnoreCase) < 0) continue;

                        int pid = Convert.ToInt32(mo["ProcessId"]);
                        all.Add(pid);
                        // The main browser process is the one without a --type=
                        // switch; killing that with taskkill /T takes the tree.
                        if (cmd.IndexOf("--type=", StringComparison.OrdinalIgnoreCase) < 0) roots.Add(pid);
                    }
                    catch (Exception ex) { Log("pid inspect failed: " + ex.Message); }
                }
            }
            catch (Exception ex)
            {
                Log("browser enumeration failed: " + ex.Message);
                return 0;
            }

            Log("uninstall: " + roots.Count + " tree root(s), " + all.Count + " process(es) matched");

            // Prefer taskkill /T on each root: it takes children with it, which
            // plain Process.Kill does not.
            foreach (int pid in roots)
            {
                killed += Taskkill(pid) ? 1 : 0;
            }
            if (killed > 0) System.Threading.Thread.Sleep(1500);

            // Sweep anything still standing, in case a root was not matched.
            foreach (int pid in all)
            {
                try
                {
                    Process p = Process.GetProcessById(pid);
                    p.Kill();
                    killed++;
                }
                catch (ArgumentException) { /* already exited */ }
                catch (Exception ex) { Log("kill pid " + pid + " failed: " + ex.GetType().Name + ": " + ex.Message); }
            }
            return killed;
        }

        private static bool Taskkill(int pid)
        {
            try
            {
                ProcessStartInfo psi = new ProcessStartInfo("taskkill.exe",
                    "/F /T /PID " + pid);
                psi.UseShellExecute = false;
                psi.CreateNoWindow = true;
                psi.RedirectStandardOutput = true;
                psi.RedirectStandardError = true;
                using (Process p = Process.Start(psi))
                {
                    string output = p.StandardOutput.ReadToEnd() + p.StandardError.ReadToEnd();
                    p.WaitForExit(10000);
                    Log("taskkill " + pid + " -> exit " + p.ExitCode + " " + output.Trim());
                    return p.ExitCode == 0;
                }
            }
            catch (Exception ex)
            {
                Log("taskkill " + pid + " threw: " + ex.Message);
                return false;
            }
        }

        // ---------- shortcuts + registry ----------

        private static void CreateShortcut(string linkPath)
        {
            try
            {
                Directory.CreateDirectory(Path.GetDirectoryName(linkPath));
                string target = File.Exists(ExePath) ? ExePath : Assembly.GetExecutingAssembly().Location;
                Shortcut.Create(linkPath, target, "--open", IconPath,
                                AppName + " - Irok web driver", InstallDir);
                Log("shortcut: " + linkPath);
            }
            catch (Exception ex) { Log("shortcut failed for " + linkPath + ": " + ex.Message); }
        }

        private static void RegisterUninstall()
        {
            try
            {
                string exe = File.Exists(ExePath) ? ExePath : Assembly.GetExecutingAssembly().Location;
                using (RegistryKey k = Registry.CurrentUser.CreateSubKey(UninstKey))
                {
                    k.SetValue("DisplayName", AppName, RegistryValueKind.String);
                    k.SetValue("DisplayVersion", Version, RegistryValueKind.String);
                    k.SetValue("Publisher", "Irok Configurator (community)", RegistryValueKind.String);
                    k.SetValue("DisplayIcon", IconPath, RegistryValueKind.String);
                    k.SetValue("InstallLocation", InstallDir, RegistryValueKind.String);
                    k.SetValue("UninstallString", "\"" + exe + "\" --uninstall", RegistryValueKind.String);
                    k.SetValue("QuietUninstallString", "\"" + exe + "\" --uninstall --silent", RegistryValueKind.String);
                    k.SetValue("URLInfoAbout", DefaultUrl, RegistryValueKind.String);
                    k.SetValue("NoModify", 1, RegistryValueKind.DWord);
                    k.SetValue("NoRepair", 1, RegistryValueKind.DWord);
                }
                Log("registered uninstall entry");
            }
            catch (Exception ex) { Log("register failed: " + ex.Message); }
        }

        // ---------- helpers ----------

        private static bool PathsEqual(string a, string b)
        {
            try { return string.Equals(Path.GetFullPath(a), Path.GetFullPath(b), StringComparison.OrdinalIgnoreCase); }
            catch { return false; }
        }

        private static void TryDelete(string path)
        {
            try { if (File.Exists(path)) File.Delete(path); }
            catch (Exception ex) { Log("delete failed " + path + ": " + ex.Message); }
        }

        private static void Info(string text, bool error)
        {
            Log((error ? "UI-ERROR: " : "UI: ") + text.Replace("\n", " "));
            if (silent) return;
            MessageBox.Show(text, error ? AppName + " - error" : AppName,
                MessageBoxButtons.OK,
                error ? MessageBoxIcon.Warning : MessageBoxIcon.Information);
        }

        private static void Log(string msg)
        {
            try
            {
                Directory.CreateDirectory(InstallDir);
                File.AppendAllText(LogPath,
                    DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + "  " + msg + Environment.NewLine);
            }
            catch { /* logging must never throw */ }
        }

        private static void PrintHelp()
        {
            string h =
                AppName + " " + Version + Environment.NewLine + Environment.NewLine +
                "  (no args)     install, then open the configurator" + Environment.NewLine +
                "  --open        open the configurator only" + Environment.NewLine +
                "  --uninstall   remove shortcuts, registry entry and files" + Environment.NewLine +
                "  --silent      no UI (for scripts)" + Environment.NewLine +
                "  --help        this text" + Environment.NewLine + Environment.NewLine +
                "Config: " + ConfigPath + Environment.NewLine +
                "  Url=            web driver address (default " + DefaultUrl + ")" + Environment.NewLine +
                "  Preferred=      edge | chrome | brave | opera | vivaldi" + Environment.NewLine +
                "  BrowserPath=    full path to a specific browser exe" + Environment.NewLine +
                "  SharedProfile=  true to use your normal browser profile" +
                " (extensions such as Dark Reader will then apply)" + Environment.NewLine +
                "  DesktopShortcut= true|false" + Environment.NewLine;
            Console.WriteLine(h);
        }
    }

    // Late-bound WScript.Shell: no reference to Microsoft.CSharp, and no hard
    // dependency on a specific interop assembly version.
    internal static class Shortcut
    {
        public static void Create(string linkPath, string target, string args,
                                  string iconPath, string description, string workDir)
        {
            Type t = Type.GetTypeFromProgID("WScript.Shell");
            object shell = Activator.CreateInstance(t);
            object link = t.InvokeMember("CreateShortcut", BindingFlags.InvokeMethod,
                null, shell, new object[] { linkPath });
            Type lt = link.GetType();
            Set(lt, link, "TargetPath", target);
            Set(lt, link, "Arguments", args);
            Set(lt, link, "WorkingDirectory", workDir);
            Set(lt, link, "IconLocation", iconPath + ",0");
            Set(lt, link, "Description", description);
            Set(lt, link, "WindowStyle", 1);
            t.InvokeMember("Save", BindingFlags.InvokeMethod, null, link, null);
            System.Runtime.InteropServices.Marshal.FinalReleaseComObject(link);
            System.Runtime.InteropServices.Marshal.FinalReleaseComObject(shell);
        }

        private static void Set(Type t, object o, string name, object value)
        {
            t.InvokeMember(name, BindingFlags.SetProperty, null, o, new object[] { value });
        }
    }

    internal sealed class Config
    {
        public string Url = Program.DefaultUrl;
        public string Preferred = "edge";
        public string BrowserPath = "";
        public bool SharedProfile = false;
        public bool DesktopShortcut = true;

        public static Config Load(string path)
        {
            Config c = new Config();
            if (!File.Exists(path)) return c;
            string[] lines;
            try { lines = File.ReadAllLines(path); }
            catch { return c; }

            foreach (string raw in lines)
            {
                string line = raw.Trim();
                if (line.Length == 0 || line.StartsWith("#")) continue;
                int i = line.IndexOf('=');
                if (i <= 0) continue;
                string k = line.Substring(0, i).Trim().ToLowerInvariant();
                string v = line.Substring(i + 1).Trim();
                switch (k)
                {
                    case "url": c.Url = v; break;
                    case "preferred": c.Preferred = v.ToLowerInvariant(); break;
                    case "browserpath": c.BrowserPath = v; break;
                    case "sharedprofile": c.SharedProfile = ToBool(v, c.SharedProfile); break;
                    case "desktopshortcut": c.DesktopShortcut = ToBool(v, c.DesktopShortcut); break;
                }
            }
            return c;
        }

        public void Save(string path)
        {
            StringBuilder sb = new StringBuilder();
            sb.Append("# Irok Configurator settings. Edit and relaunch to apply.\n");
            sb.Append("Url=").Append(Url).Append('\n');
            sb.Append("Preferred=").Append(Preferred).Append('\n');
            sb.Append("BrowserPath=").Append(BrowserPath).Append('\n');
            sb.Append("SharedProfile=").Append(SharedProfile ? "true" : "false").Append('\n');
            sb.Append("DesktopShortcut=").Append(DesktopShortcut ? "true" : "false").Append('\n');
            File.WriteAllText(path, sb.ToString());
        }

        private static bool ToBool(string v, bool fallback)
        {
            if (v.Equals("true", StringComparison.OrdinalIgnoreCase) || v == "1" ||
                v.Equals("yes", StringComparison.OrdinalIgnoreCase)) return true;
            if (v.Equals("false", StringComparison.OrdinalIgnoreCase) || v == "0" ||
                v.Equals("no", StringComparison.OrdinalIgnoreCase)) return false;
            return fallback;
        }
    }
}
