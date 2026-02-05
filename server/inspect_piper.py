try:
    from piper import PiperVoice
    import inspect
    print("PiperVoice class structure:")
    print(dir(PiperVoice))
    print("\nPiperVoice.synthesize signature:")
    # print(inspect.signature(PiperVoice.synthesize)) # Might fail if it's a binding
    print(PiperVoice.synthesize.__doc__)
except Exception as e:
    print(f"Error: {e}")
