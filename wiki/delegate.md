# Delegate with `arky`

## `hot@dark/delegate> ?`

```
Usage: delegate link [<secret> <2ndSecret>]
       delegate save <name>
       delegate unlink
       delegate status
       delegate voters

Subcommands:
    link   : link to delegate using secret passphrases. If secret passphrases
             contains spaces, it must be enclosed within double quotes
             ("secret with spaces"). If no secret given, it tries to link
             with saved account(s).
    save   : save linked delegate to a *.tokd file.
    unlink : unlink delegate.
    status : show information about linked delegate.
    voters : show voters contributions ([address - vote] pairs).
```
