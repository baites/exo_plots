## [root.style.py](https://github.com/ksamdev/exo_plots/blob/master/root/style.py)

Definition of ROOT styles to be applied to all the plots. The module defines
nest styles:

* **analysis** should be applied to the daily analysis plots and should match
the Analysis Note requirements
* **pas** is a Physics Analysis Summary plots style

## Use

Make sure the style is loaded and applied first in the script before any plot
is generated or loaded from file(s), e.g.:

```python
import ROOT

from root import style

an_style = style.analysis()
an_style.cd()
ROOT.gROOT.ForceStyle()
```
