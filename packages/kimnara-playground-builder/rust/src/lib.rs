use std::collections::HashMap;
use std::io::ErrorKind;
use std::path::{Path, PathBuf};
use std::process::Command;

use anyhow::Error;
use pyo3::{PyResult, pymodule};
use pyo3::exceptions::PyKeyError;
use rattler_conda_types::Platform;
use rattler_lock::LockFile;
use rattler_shell::activation::{ActivationVariables, Activator};
use rattler_shell::shell::{Bash, ShellEnum};
use serde::Deserialize;

#[derive(Deserialize)]
struct EnvironmentInfo {
    name: String,
    platforms: Vec<Platform>,
    prefix: PathBuf,
}

#[derive(Deserialize)]
struct Info {
    environments_info: Vec<EnvironmentInfo>,
}

mod subprocess {
    pyo3::import_exception!(subprocess, CalledProcessError);
}

mod rattler {
    pyo3::import_exception!(rattler.exceptions, ActivationError);
    pyo3::import_exception!(rattler.exceptions, ParseCondaLockError);
}

#[pyo3::pyfunction]
fn inspect() -> PyResult<HashMap<String, HashMap<String, String>>> {
    let output = Command::new("pixi")
        .args(["-vvv", "info", "--json"])
        .output()?;

    if !output.status.success() {
        let pyerr = subprocess::CalledProcessError::new_err((
            output.status.code(),
            ["pixi", "-vvv", "info", "--json"],
            String::from_utf8(output.stdout).ok(),
            String::from_utf8(output.stderr).ok(),
        ));
        return Err(pyerr);
    }

    let info: Info = serde_json::from_slice(&output.stdout).map_err(
        |err| std::io::Error::new(ErrorKind::InvalidData, err.to_string()),
    )?;

    let variables = ActivationVariables::from_env().unwrap_or_default();
    info.environments_info
        .into_iter()
        .filter(|env| env.platforms.contains(&Platform::current()))
        .map(|env| {
            let shell_type = if cfg!(not(target_os = "windows")) {
                ShellEnum::default()
            } else if env.name == "gcc" {
                Bash::default().into()
            } else {
                ShellEnum::default()
            };

            Activator::from_path(&env.prefix, shell_type, Platform::current())
                .and_then(|shell| shell.run_activation(variables.clone(), None))
                .map(|value| (env.name, value))
                .map_err(|err| rattler::ActivationError::new_err(
                    format!("{:#}", Error::new(err)),
                ))
        })
        .collect()
}

#[pyo3::pyfunction]
fn numba_versions() -> PyResult<HashMap<String, String>> {
    LockFile::from_path(Path::new("pixi.lock"))
        .map_err(|err| rattler::ParseCondaLockError::new_err(
            format!("{:#}", Error::new(err)),
        ))?
        .environments()
        .filter_map(|(name, env)| if name.starts_with("nb") {
            let (_, packages) = env.packages_by_platform().find(
                |(platform, _)| platform.subdir() == Platform::current(),
            )?;
            if let Some(data) = packages
                .filter_map(|package| package.as_binary_conda())
                .find(|data| data.package_record.name.as_source() == "numba")
            {
                let version = data.package_record.version.to_string();
                Some(Ok((name.into(), version)))
            } else {
                Some(Err(PyKeyError::new_err("numba")))
            }
        } else {
            None
        })
        .collect()
}

#[pymodule]
mod _env {
    #[pymodule_export]
    use super::inspect;

    #[pymodule_export]
    use super::numba_versions;
}
