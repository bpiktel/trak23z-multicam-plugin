# Blender Multi Camera Rendering Plugin

## Installation

In order to use the plugin in Blender you need to install it.

In Blender, head to `Edit` > `Preferences...` > `Add-ons` and click `Install` in the upper right corner of the window.

Now find the plugin file in the files tree and click `Install Add-on`.
Make sure to enable it by checking the box next to the add-on name on the list.

You're set to work with the plugin! Enjoy!


## Plugin features walkthrough

In order to reach the features added by the plugin select a camera and head to `Data` section of its properties.
You'll see `Multi camera properties` tab with four buttons, which allow to switch between different camera modes.

![General plugin tab](./docs/images/plugin-tab.png)


### Single camera

![Single camera mode](./docs/images/modes/single/single-mode.png)

This one is just a basic Blender camera you know and love.
Its main use is to revoke all the changes made in different modes.


### Stereo camera

![stereo camera mode](./docs/images/modes/stereo/stereo-mode.png)

The stereo mode creates two sub-cameras based on the main camera you've chosen earlier.

In default configuration they face the same direction as the base camera.
You can decide how far away from each other the cameras are by manipulating the `Cameras spacing` attribute.

![stereo camera mode - spacing 20](./docs/images/modes/stereo/stereo-spacing-20.png)
In the picture above the spacing is set to default 20 units.


![stereo camera mode  - spacing 200](./docs/images/modes/stereo/stereo-spacing-200.png)
In the picture above the spacing is set to 200 units.


There is a possibility to make the camera axis converge, by checking the `Convergent` box.
Now you'll see additional attribute - `Zero parallax`.
It determines how far from the base camera the stereo cameras' axis converge.

![stereo camera mode - convergent check](./docs/images/modes/stereo/stereo-convergent-mode.png)

![stereo camera mode - spacing 200, parallax 200](./docs/images/modes/stereo/stereo-convergent-parallax-200.png)
In the picture above both the spacing and zero parallax are set to 200 units.


![stereo camera mode - spacing 200, parallax 600](./docs/images/modes/stereo/stereo-convergent-parallax-600.png)
In the picture above the spacing is set to 200 units, but parallax has been changed to 600.


### Matrix camera
![matrix camera mode](./docs/images/modes/matrix/matrix-mode.png)

Another mode available in the plugin is the matrix mode.
It allows to create a matrix of parallel sub-cameras, based on the selected camera.

You can decide:
* how many cameras are there in each direction (`Vertical amount` and `Horizontal amount` parameters).
* how far away are the cameras from each other (`Vertical distance` and `Horizontal distance` parameters).

_⚠️ Note that the matrix will be built upwards and to the right from the base camera (when looking from behind it)._

![matrix camera mode - amount (3, 3), distance (100, 100)](./docs/images/modes/matrix/matrix-3-3-100-100.png)
In the picture above the amount and distance parameters were set to (3, 3) and (100, 100) respectively.

![matrix camera mode - amount (3, 3), distance (200, 300)](./docs/images/modes/matrix/matrix-3-3-200-300.png)
In the picture above the amount and distance parameters were set to (3, 3) and (200, 300) respectively.

![matrix camera mode - amount (5, 7), distance (100, 100)](./docs/images/modes/matrix/matrix-5-7-100-100.png)
In the picture above the amount and distance parameters were set to (5, 7) and (100, 100) respectively.


#### [Light field camera](https://en.wikipedia.org/wiki/Light_field_camera)

If you want to achieve the light field camera effect you should set the distance attributes to small values.

![matrix camera mode - light field](./docs/images/modes/matrix/matrix-15-15-20-20.png)
In the picture above the amount and distance parameters were set to (15, 15) and (20, 20) respectively.
