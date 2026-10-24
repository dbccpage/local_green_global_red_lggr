import Lake
open Lake DSL

/- The cache is shipped with this package; this configuration never fetches.
   Source files, pins, licenses and hashes accompany every compiled module. -/
package «rsi_mathlib_vendor» where
  buildDir := run_io do
    let here : System.FilePath := __dir__
    let destination := here / ".." / ".lake" / "vendor"
    if !(← (destination / "READY").pathExists) then
      IO.FS.createDirAll destination
      let result ← IO.Process.output {
        cmd := "tar"
        args := #["-xzf", (here / "dependencies.tar.gz").toString, "-C", destination.toString]
      }
      if result.exitCode != 0 then
        throw (IO.userError s!"Offline Lean cache extraction failed: {result.stderr}")
    let absolute ← IO.FS.realPath destination
    pure (if System.Platform.isWindows then
      System.FilePath.mk ("\\\\?\\" ++ absolute.toString) else absolute)
  leanLibDir := "lib"
