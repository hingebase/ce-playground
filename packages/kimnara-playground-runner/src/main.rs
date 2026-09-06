use std::process::ExitCode;

use rattler_shell::run_command_in_environment;

#[cfg(target_os = "windows")]
const LIBRARY_BIN: &str = "Library/bin";

#[cfg(not(target_os = "windows"))]
const LIBRARY_BIN: &str = "bin";

#[tokio::main(flavor = "current_thread")]
async fn main() -> anyhow::Result<ExitCode> {
    let mut prefix = std::env::current_exe()?;
    if !(prefix.pop() && prefix.ends_with(LIBRARY_BIN)) {
        return Ok(ExitCode::FAILURE);
    }
    prefix.pop();  // bin
    if cfg!(target_os = "windows") {
        prefix.pop();  // Library
    }

    let mut base = prefix.with_file_name("conda");
    if cfg!(target_os = "windows") {
        // condabin doesn't work
        base.push("Scripts");
    } else {
        // Prefer condabin which is minimal
        base.push("condabin");
    }
    if let Some(path) = std::env::var_os("PATH") {
        let mut paths: Vec<_> = std::env::split_paths(&path).collect();
        paths.insert(0, base);
        let new_path = std::env::join_paths(paths)?;
        unsafe { std::env::set_var("PATH", &new_path); }
    } else {
        unsafe { std::env::set_var("PATH", &base); }
    }

    let mut command: Vec<_> = std::env::args().collect();
    command[0] = "python".into();

    let shell = Default::default();
    let env_vars = Default::default();
    run_command_in_environment(&prefix, &command, shell, &env_vars, None)
        .await?
        .code()
        .map_or(Ok(ExitCode::FAILURE), |code| Ok(u8::try_from(code)?.into()))
}
