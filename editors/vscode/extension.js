// God Code VS Code extension. Run and check .god files from the editor.
// Requires the God Code interpreter: pip install godcode-engine
const vscode = require('vscode');
const { exec } = require('child_process');

function findGodCode() {
  // Try the `godcode` CLI first, then `python3 -m godcode`, then `python -m godcode` (Windows).
  return new Promise((resolve) => {
    exec('godcode --help', (err) => {
      if (!err) return resolve('godcode');
      exec('python3 -m godcode --help', (err2) => {
        if (!err2) return resolve('python3 -m godcode');
        exec('python -m godcode --help', (err3) => {
          resolve(err3 ? null : 'python -m godcode');
        });
      });
    });
  });
}

async function runGodCode(checkOnly) {
  const editor = vscode.window.activeTextEditor;
  if (!editor || editor.document.languageId !== 'godcode') {
    vscode.window.showWarningMessage('Open a God Code (.god) file first.');
    return;
  }
  await editor.document.save();
  const bin = await findGodCode();
  if (!bin) {
    vscode.window.showErrorMessage(
      'God Code interpreter not found. Install it with: pip install godcode-engine'
    );
    return;
  }
  const file = editor.document.fileName;
  const cmd = checkOnly ? `${bin} check "${file}"` : `${bin} run "${file}"`;
  const out = vscode.window.createOutputChannel('God Code');
  out.show(true);
  out.appendLine(`$ ${cmd}`);
  exec(cmd, { timeout: 60000 }, (err, stdout, stderr) => {
    if (stdout) out.append(stdout);
    if (stderr) out.append(stderr);
    if (err) out.appendLine(`[exited with code ${err.code}]`);
    else out.appendLine('[ASCEND] Complete. 🕊');
  });
}

function activate(context) {
  context.subscriptions.push(
    vscode.commands.registerCommand('godcode.runFile', () => runGodCode(false)),
    vscode.commands.registerCommand('godcode.checkFile', () => runGodCode(true)),
    vscode.commands.registerCommand('godcode.debugFile', debugGodCode),
    vscode.debug.registerDebugAdapterDescriptorFactory('godcode', {
      createDebugAdapterDescriptor: async () => {
        const bin = await findGodCode();
        if (!bin) {
          vscode.window.showErrorMessage(
            'God Code interpreter not found. Install it with: pip install godcode-engine'
          );
          return null;
        }
        const parts = bin.split(' ');
        return new vscode.DebugAdapterExecutable(parts[0], [...parts.slice(1), 'dap']);
      },
    })
  );
}

async function debugGodCode() {
  const editor = vscode.window.activeTextEditor;
  if (!editor || editor.document.languageId !== 'godcode') {
    vscode.window.showWarningMessage('Open a God Code (.god) file first.');
    return;
  }
  await editor.document.save();
  vscode.debug.startDebugging(undefined, {
    type: 'godcode',
    request: 'launch',
    name: 'Debug God Code',
    program: editor.document.fileName,
    stopOnEntry: true,
  });
}

function deactivate() {}

module.exports = { activate, deactivate };
