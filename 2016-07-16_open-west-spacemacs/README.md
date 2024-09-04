# Spacemacs: The Best of Both the Emacs and Vim Worlds

Talk given at the [Open West Conference 2016](https://web.archive.org/web/20190420031712/https://openwest.org/past/2016/index.html) on July 16, 2016 as an introduction to [Spacemacs](https://github.com/syl20bnr/spacemacs).

## Meta

The [slides](presentation.org) are written in [Org Mode](https://orgmode.org) using [org-present](https://github.com/rlister/org-present).

I used the following Emacs Lisp from [my old Emacs configuration](https://github.com/travisbhartwell/vcsh_emacs/blob/master/.spacemacs.d/bashombp.el#L89-L102) to start the presentation:

```elisp
(defun tbh/start-presentation ()
  (interactive)
  (spacemacs/load-theme 'spacemacs-light)
  (spacemacs/toggle-vi-tilde-fringe-off)
  (spacemacs/toggle-line-numbers-off)
  (spacemacs/toggle-maximize-buffer)
  (spacemacs/toggle-fill-column-indicator-off)
  (spacemacs/toggle-frame-fullscreen)
  (spacemacs/toggle-fringe-off)
  (find-file "/Users/travisbhartwell/Projects/Presentations/2016-07-16_open-west-spacemacs/presentation.org")
  (spacemacs/toggle-mode-line-off)
  (read-only-mode)
  (goto-char (point-min))
  (org-present))
```
