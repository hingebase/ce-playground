use std::collections::HashMap;
use std::process::ExitCode;

use rattler_shell::run_command_in_environment;

#[cfg(target_os = "windows")]
const LIBRARY_BIN: &str = "Library/bin";

#[cfg(not(target_os = "windows"))]
const LIBRARY_BIN: &str = "bin";

#[tokio::main(flavor = "current_thread")]
async fn main() -> ExitCode {
    let Ok(mut prefix) = std::env::current_exe() else {
        return ExitCode::FAILURE;
    };
    if !(prefix.pop() && prefix.ends_with(LIBRARY_BIN)) {
        return ExitCode::FAILURE;
    }
    prefix.pop();  // bin

    let cuda_home = if cfg!(target_os = "windows") {
        prefix.pop();  // Library
        let mut cuda_home = prefix.with_file_name("cuda");
        cuda_home.push("Library");
        cuda_home
    } else {
        prefix.with_file_name("cuda")
    };

    // https://github.com/compiler-explorer/compiler-explorer/issues/5481
    let env_vars = if cuda_home.is_dir() {
        cuda_home.into_string().map_or_default(
            |value| HashMap::from([("CUDA_HOME".into(), value)]),
        )
    } else {
        HashMap::new()
    };

    let mut command: Vec<_> = std::env::args().collect();
    command[0] = "python".into();

    let shell = Default::default();
    run_command_in_environment(&prefix, &command, shell, &env_vars, None)
        .await
        .ok()
        .and_then(|status| status.code())
        .and_then(|code| u8::try_from(code).ok())
        .map_or(ExitCode::FAILURE, |code| code.into())
}
