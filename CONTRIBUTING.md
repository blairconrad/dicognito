# How to Contribute

First of all, thank you for wanting to contribute to dicognito! We really appreciate any support we get from
our community. We want to keep it as easy as possible for you to contribute changes that make dicognito
better for you. There are a few guidelines that we need contributors to follow so that we can all work
together happily.

## Preparation

Before starting work on a functional change, like a new feature, a change to an existing feature, or a bug
fix, please ensure an [issue](https://github.com/dicognito/dicognito/issues) has been raised. Indicate your
intention to work on the issue by writing a comment against it. This will prevent duplication of effort. If
the change is non-trivial, it's usually best to propose a design in the issue comments.

It is not necessary to raise an issue for non-functional changes such as refactoring, adding tests,
reformatting code, documentation, updating packages, etc.

## Tests

Changes in functionality (new features, changed behavior, or bug fixes) should be described by new or
updated tests.

## Style

We use [Ruff](https://ruff.rs/) as linter and formatter.
Please follow existing conventions. Any deviations will cause the build to fail.

## Making Changes

Dicognito uses the git branching model known as [GitHub flow](https://help.github.com/articles/github-flow/).
As such, all development must be performed on a
["feature branch"](https://martinfowler.com/bliki/FeatureBranch.html) created from the main development
branch, which is called `main`. To submit a change:

1. [Fork](https://help.github.com/forking/) the
   [dicognito repository](https://github.com/blairconrad/dicognito/) on GitHub
1. Clone your fork locally
1. Configure the upstream repo (`git remote add upstream git://github.com/blairconrad/dicognito.git`)
1. Create a local branch (`git checkout -b my-branch main`)
1. Work on your feature
1. Rebase if required (see "Handling Updates from upstream/main" below)
1. Ensure the build and tests succeed (see ["How to build"](how_to_build.md "How to build"))
1. Push the branch up to GitHub (`git push origin my-branch`)
1. Send a [pull request](https://help.github.com/articles/using-pull-requests) on GitHub

You should **never** work directly on the `main` branch and you should **never** send a pull request from
the `main` branch - always from a feature branch.

## Handling Updates from upstream/main

While you're working away in your branch it's quite possible that your upstream/main (most likely the
canonical dicognito version) may be updated. If this happens you should:

1. [Stash](https://git-scm.com/book/en/v2/Git-Tools-Stashing-and-Cleaning) any un-committed changes you
   need to
1. `git checkout main`
1. `git pull upstream main`
1. `git checkout my-branch`
1. `git rebase main my-branch`
1. `git push origin main` - (optional) this makes sure your remote main branch is up to date
1. if you previously pushed your branch to your origin, you need to force push the rebased branch -
   `git push origin my-branch --force-with-lease`

This ensures that your history is "clean". That is, you have one branch off from main followed by your
changes in a straight line. Failing to do this ends up with several "messy" merges in your history, which we
don't want. This is the reason why you should always work in a branch and you should never be working in, or
sending pull requests from, main.

If you're working on a long-running change then you may want to do this quite often, rather than run the
risk of potential large merge conflicts further down the line.

## Sending a Pull Request

While working on your feature you may well create several branches, which is fine, but before you send a
pull request you should ensure that you have rebased back to a single feature branch. We care about your
commits and we care about your feature branch but we don't care about how many or which branches you created
while you were working on it. :smile:

When you're ready to go you should confirm that you are up to date and rebased with upstream/main (see
"Handling Updates from upstream/main" above) and then:

1. `git push origin my-branch`
1. Send a [pull request](https://help.github.com/articles/using-pull-requests) in GitHub, selecting the
   following dropdown values:

| Dropdown      | Value                                             |
|---------------|---------------------------------------------------|
| **base fork** | `blairconrad/dicognito`                           |
| **base**      | `main`                                          |
| **head fork** | `{your fork}` (e.g. `{your username}/dicognito`)  |
| **compare**   | `my-branch`                                       |

The pull request should include a description starting with "Fixes #12345." (using the real issue number, of
course) if it fixes an issue. If there's no issue, be sure to clearly explain the intent of the change.
