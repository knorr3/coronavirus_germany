[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
# Corona Germany Homeassistant Sensor
Gets the latest corona stats from the RKI API integration.

<img src="https://i.imgur.com/2GQ6LWy.png" alt="Coronavirus Sensor" width="300px">


## Installation
### 1. Using HACS (recommended way)

Open your HACS Settings and add

https://github.com/knorr3/coronavirus_germany

as custom repository URL.

Then install the "Corona Germany" integration.

If you use this method, your component will always update to the latest version.

### 2. Manual
Place a copy of:

[`__init__.py`](custom_components/corona_germany/__init__.py) at `<config>/custom_components/corona_germany/__init__.py`  
[`sensor.py`](custom_components/corona_germany/sensor.py) at `<config>/custom_components/corona_germany/sensor.py`  
[`manifest.json`](custom_components/corona_germany/manifest.json) at `<config>/custom_components/corona_germany/manifest.json`
and so on, with every other file

where `<config>` is your Home Assistant configuration directory.

>__NOTE__: Do not download the file by using the link above directly. Rather, click on it, then on the page that comes up use the `Raw` button.

## Configuration 

### Configuration Variables
- **entity_id**: Choose your location 
it will most likely begin with LK (Landkreis) or SK (Stadtkreis). 
Examples: SK München, LK Ebersberg, LK Wolfratshausen

## Examples

For a better look-and-feel you'll need to install [lovelace-multiple-entity-row](https://github.com/benct/lovelace-multiple-entity-row) (available on HACS), create a bunch of sensors and then use a configuration similar to this for each sensor:

``` yaml
- type: custom:multiple-entity-row
  entity: sensor.coronavirus_yourlocation
  entities:
    - attribute: cases
      name: Cases
    - attribute: deaths
      name: Deaths
    - attribute: incidence
      name: Incidence
  show_state: false
  icon: 'mdi:biohazard'
  name: München
  secondary_info: last-changed
```

## Thanks to
Huge thanks to `@boralyl` for the project structure!

Check out their repository:

https://github.com/boralyl/github-custom-component-tutorial

Also huge thanks to `@FaserF` for the inspiration!
