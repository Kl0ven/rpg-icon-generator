# RPG icon generator

This package generate RPG items images procedurally, based on [BrianMacIntosh Algoritms](https://github.com/BrianMacIntosh/icon-machine)

## Item type
  - [x] Blade
  - [x] Potion
  - [ ] Masses
  - [ ] Axe
  - More to come ;)

## Output example
| Complexity | Rarity equivalent | Blade Examples | Potion Examples |
| ---------- | ----------------- | -------------- | --------------- |
|0           | Common Low       |![Blade_0](https://raw.githubusercontent.com/Kl0ven/rpg-icon-generator/master/docs/blades/blade_0.png)    |![Potion_0](https://raw.githubusercontent.com/Kl0ven/rpg-icon-generator/master/docs/potions/potion_0.png)|
|40          | Common High      |![Blade_40](https://raw.githubusercontent.com/Kl0ven/rpg-icon-generator/master/docs/blades/blade_40.png)  |![Potion_40](https://raw.githubusercontent.com/Kl0ven/rpg-icon-generator/master/docs/potions/potion_40.png)|
|41          | Uncommon Low     |![Blade_41](https://raw.githubusercontent.com/Kl0ven/rpg-icon-generator/master/docs/blades/blade_41.png)  |![Potion_41](https://raw.githubusercontent.com/Kl0ven/rpg-icon-generator/master/docs/potions/potion_41.png)|
|60          | Uncommon High    |![Blade_60](https://raw.githubusercontent.com/Kl0ven/rpg-icon-generator/master/docs/blades/blade_60.png)  |![Potion_60](https://raw.githubusercontent.com/Kl0ven/rpg-icon-generator/master/docs/potions/potion_60.png)|
|61          | Rare Low         |![Blade_61](https://raw.githubusercontent.com/Kl0ven/rpg-icon-generator/master/docs/blades/blade_61.png)  |![Potion_61](https://raw.githubusercontent.com/Kl0ven/rpg-icon-generator/master/docs/potions/potion_61.png)|
|85          | Rare High        |![Blade_85](https://raw.githubusercontent.com/Kl0ven/rpg-icon-generator/master/docs/blades/blade_85.png)  |![Potion_85](https://raw.githubusercontent.com/Kl0ven/rpg-icon-generator/master/docs/potions/potion_85.png)|
|86          | Epic Low         |![Blade_86](https://raw.githubusercontent.com/Kl0ven/rpg-icon-generator/master/docs/blades/blade_86.png)  |![Potion_86](https://raw.githubusercontent.com/Kl0ven/rpg-icon-generator/master/docs/potions/potion_86.png)|
|95          | Epic High        |![Blade_95](https://raw.githubusercontent.com/Kl0ven/rpg-icon-generator/master/docs/blades/blade_95.png)  |![Potion_95](https://raw.githubusercontent.com/Kl0ven/rpg-icon-generator/master/docs/potions/potion_95.png)|
|96          | Outstanding Low  |![Blade_96](https://raw.githubusercontent.com/Kl0ven/rpg-icon-generator/master/docs/blades/blade_96.png)  |![Potion_96](https://raw.githubusercontent.com/Kl0ven/rpg-icon-generator/master/docs/potions/potion_96.png)|
|100         | Outstanding High |![Blade_100](https://raw.githubusercontent.com/Kl0ven/rpg-icon-generator/master/docs/blades/blade_100.png)|![Potion_100](https://raw.githubusercontent.com/Kl0ven/rpg-icon-generator/master/docs/potions/potion_100.png)|



## instalation 

```
pip install rpg-icon-generator
```
## Usage

```python
from rpg_icon_generator import Blade_Generator
generator = Blade_Generator()
seed = datetime.now() # provide a seed for this blade 

# the image will be in test/out/[seed].png
# the image will be 32*2 by 32*2 pixels
# complexity ranging from 0 to 100
generator.generate(seed=seed, complexity=50, dimension=32, render_scale=2, output_directory='test/out/')
```

```python
# Same for the other generator
from rpg_icon_generator import Potion_Generator

```
