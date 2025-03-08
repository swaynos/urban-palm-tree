# urban-palm-tree
Automate gameplay on your PS5 by capturing the stream, analyzing frames, and making decisions based on game elements. This project leverages existing software to stream the PS5 feed to your computer and capture keyboard input to send back to the console.

## Table of Contents
- Installation
- Usage
- Contributing
- License

## Installation
1. Clone the repository:
    ```bash
    git clone git@github.com:swaynos/urban-palm-tree.git
    ```

2. Install Python dependencies using Poetry:
    ```bash
    poetry install
    ```

## Usage
- Run the project using the following command:
    ```bash
    poetry run python main.py
    ```

## Contributing
1. Fork the repository.
2. Create a new branch: `git checkout -b feature-name`.
3. Make your changes.
4. Push your branch: `git push origin feature-name`.
5. Create a pull request.

## TODO
- [ ] Run inference on the new Rush model
- [ ] Build the set of player actions that the bot can perform. Immediately, this will be pass, shoot, and move.
- [X] Optimize the inference time. The time between when the screenshot is captured to when an action is performed.
- [ ] Build another model that will take the output of the Rush model and determine the best action to perform.

## Notes
 - InferenceSteps modify their chain at the end of the infer() step.
 ```
    # From here the pipeline can be modified based on the game state
    # old_next_step = self.next_step
    # new_next_step = NewInferenceStep()
    # new_next_step.set_next(old_next_step)
    # self.set_next(new_next_step)
```

## License
This project is licensed under the GNU General Public License v3.0

## Project Goals
1. While playing Rush in FC25, keep the player active by performing actions on behalf of the user.
2. Introduce reinforcement learning to optimize the actions performed by the bot.
