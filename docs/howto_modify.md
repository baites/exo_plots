## Summary

This is the open-source project and anyone is welcome to contribute. You
may find a nice description of the Git work flow at
[GitHub:Help](https://help.github.com/articles/fork-a-repo) with instructions
on how to contribute to the project.

Short summary of the same instructions is given below. It is assumed that
you are familiar with [Git basics](http://git-scm.com/documentation). Read
first three chapters to refresh the knowledge in the book at the reference.

## HowTo

- register on GitHub if you don't have an account yet
- fork repository:
    - go to project main page [exo_plots](https://github.com/ksamdev/exo_plots)
    - press **fork** button in the top-right corner (this will create
      your "copy" of the project)
- clone repository to your machine:

```bash
git clone URL_TO_YOUR_FORK
```

- change the code and push back to GitHub to your repo:

```bash
# change the code
git commit -m "your first change" -a
# change the code
# ...
# push changes to GitHub
git push origin master
```

- Create pull request: go to your fork (copy of the project on GitHub) and
press **pull request** button in the top right corner
- The administrator of the original project will be notified about changes and
propagate your fixes/new features to the main repository
