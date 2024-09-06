**USAGE**

For everything to work properly, the first step is to create a `.env` file in the same directory as the `main.py` file. Inside this file, create te variable `TOKEN` as following:

```
TOKEN = <token-string>
```

The `<token-string>` must be a canvas-generated token. You can create one by following the steps:

1. Go to "account > settings"
2. Scroll down until you find "Approved Integrations"
3. Click "+ Create Access Token"
4. Write a purpose and an expiration date, then click "Generate Token"
5. Copy the token, this will only appear once and if you lose it, you'll have to generate another.
6. The token you just generated is the one you have to write in the `.env` file

Once you have that ready, you should be able to execute the program using `python main.py <Course code>`. You can check other optional arguments by running `python main.py --help`.

**Alias for easy usage**

I understand that using this from the folder you cloned the repo and trying to update or download the files of a course in a very different folder can be a little tedious. In order to fix that, you can set up an alias so you can execute the file in a more simple way from any directory you're in. If you're using linux or wsl you can follow these steps:

1. Find out what shell you're using. You're probably using a `bash` shell, but you may have a `zsh` shell.
2. Once you are sure about which shell you have, open the `.bashrc` or `.zshrc` file in your home directory
3. Add a line line the following: `alias your-alias='python /path/to/file/main.py`.
4. You can close and reopen the terminal or just use `source ~/.bashrc` (in case you're using a bash shell).
5. You should be ready to use the script anywhere you are.

If you're using MAC, you may be able to do something very similar, but since I don't have access to one, I cannot confirm the exact steps.
If you're using windows, good luck figuring it out.
