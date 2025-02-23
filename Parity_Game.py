import json
from tulip import spec, synth
from LLM_LTL_Transformation import * 

def Call_LLM(Game_File):
    # Modify this so that any LLM can be called, currently fixed to use Claude.
    LLM = ClaudeAIClient()
    LLM.FormalizeGame(Game_File)

def Parity_Game():
    # Read and parse the JSON input.
    with open('Reactive_Synthesis_Input.json', 'r') as f:
        data = json.load(f)
    
    # Retrieve fields from the JSON.
    ltl_formulation = data['ltl_formulation']
    system_player = data["System_Player"]
    environment_player = data.get("Environment_Player", {})
    inputs = data["Inputs"]
    outputs = data["Outputs"]
    
    # Check the type of environment_player
    if isinstance(environment_player, str):
        print("Error: Environment_Player is a string, expected a dictionary.")
        return

    # Build a GRSpec object.
    # It is assumed that:
    # - inputs and outputs are dictionaries mapping variable names to their domains,
    # - system_player and environment_player are dictionaries containing keys like "init", "safety", "prog".
    grspec = spec.GRSpec(
        env_vars=inputs,
        sys_vars=outputs,
        env_init=environment_player.get("init", []),
        env_safety=environment_player.get("safety", []),
        env_prog=environment_player.get("prog", []),
        sys_init=system_player.get("init", []),
        sys_safety=system_player.get("safety", []),
        sys_prog=system_player.get("prog", [])
    )
    
    # Incorporate the overall LTL formulation as an additional system safety condition.
    # (Adjust this if your specification separates assumptions and guarantees differently.)
    grspec.sys_safety.append(ltl_formulation)
    
    # Create an LTL specification object
    ltl_spec = spec.LTL(ltl_formulation)  # Assuming ltl_formulation is a valid LTL string

    # Synthesize a controller using Tulip.
    controller = synth.synthesize(grspec, specs=ltl_spec)
    
    if controller is None:
        print("The specification is unrealizable.")
        return "unrealizable"
    else:
        print("The specification is realizable.")
        # Optionally, save or visualize the synthesized controller.
        controller.save('controller.png')
        return "realizable"

if __name__ == '__main__':
    results = Parity_Game()
    print("Result:", results)
