from openai import OpenAI

if __name__ == '__main__':
    # Open connection to Ollama using OpenAI client
    client = OpenAI(
        base_url='http://localhost:11434/v1/',
        api_key='ollama',
    )
    
    prompt = "What's the formula for energy?"

    
    response = client.chat.completions.create(
        model='gemma:2b',
        temperature=0.0, # set temperature parameter to 0
        messages=[{"role": "user", "content": prompt}],
    )

    print(response.choices[0].message.content)
    print('\n\nEND PROMPT\n\n')
    
    for r in response:
        print(r)
    
    # ('id', 'chatcmpl-538')
    # ('choices', [Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content="Sure, here's the formula for energy:\n\n**E = K + U**\n\nWhere:\n\n* **E** is the energy in joules (J)\n* **K** is the kinetic energy in joules (J)\n* **U** is the potential energy in joules (J)\n\n**Kinetic energy (K)** is the energy an object possesses when it moves or is in motion. It is calculated as half the product of an object's mass (m) and its velocity (v) squared:\n\n**K = 1/2 * m * v^2**\n\n**Potential energy (U)** is the energy an object possesses when it is in a position or has a specific configuration. It is calculated as the product of an object's mass and the gravitational constant (g) multiplied by the height or distance of the object from a reference point.\n\n**Gravitational potential energy (U)** is given by the formula:\n\n**U = mgh**\n\nWhere:\n\n* **m** is the mass of the object in kilograms (kg)\n* **g** is the acceleration due to gravity in meters per second squared (m/s^2)\n* **h** is the height or distance of the object in meters (m)\n\nThe formula for energy can be used to calculate the total energy of an object, the energy of a specific part of an object, or the change in energy of an object over time.", role='assistant', function_call=None, tool_calls=None))])
    # ('created', 1719865480)
    # ('model', 'gemma:2b')
    # ('object', 'chat.completion')
    # ('service_tier', None)
    # ('system_fingerprint', 'fp_ollama')
    # ('usage', CompletionUsage(completion_tokens=304, prompt_tokens=0, total_tokens=304))