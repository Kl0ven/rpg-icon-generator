# RPG icon generator

This package generate RPG items images procedurally, based on [BrianMacIntosh Algoritms](https://github.com/BrianMacIntosh/icon-machine)

## Item type
  - [x] Blade
  - [ ] Potion
  - [ ] Masses
  - [ ] Axe
  - More to come ;)

## Output example
### Blades
![Blade_1](https://raw.githubusercontent.com/Kl0ven/rpg-icon-generator/master/docs/Blade_1.png) ![Blade_2](https://raw.githubusercontent.com/Kl0ven/rpg-icon-generator/master/docs/Blade_2.png) ![Blade_3](https://raw.githubusercontent.com/Kl0ven/rpg-icon-generator/master/docs/Blade_3.png)


## Usage

```python
from rpg_icon_generator import Blade_Generator
generator = Blade_Generator()
seed = datetime.now() # provide a seed for this blade 

# the image will be in test/out/[seed].png
generator.generate(seed=seed, dimension=32, output_directory='test/out/')
```