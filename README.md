# openid_login_cmd
A simple cli app to execute OIDC login workflow.

## Disclaimer
1. For now only supports `authorization_code` workflow (which was my use case at the moment)

## Installation
Clone the repository, `cd` in the directory and run `python setup.py install`. An executable will be generated in the path ([setuptools entry_point](https://setuptools.readthedocs.io/en/latest/userguide/entry_point.html#console-scripts)), you can check if it's installed with `oidc-login --help`.

The first time it runs it will create a default config in `~/.openid-cmd/config.yml` (if not exists yet or if you do not provide a config file path with argument `-c`). Config format:
```yml
openid_client:
  auth_redirect_url: https://auth.mydom.com/oauth2/auth
  token_url: https://auth.mydom.com/oauth2/token
  response_type: code
  grant_type: authorization_code
  client_id: native-cli
  redirect_port: 55145 # A socket will be opened in this port and redirect uri will be 'http://localhost:{redirect_port}'
  scope: 'openid offline_access'

browser:
  cmd: firefox # command to launch browser (firefox, chrome, chromium, etc)

output: # values to print from openid server token response
  - access_token
  - refresh_token
  - token_type
  - id_token
```