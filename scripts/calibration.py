#!/usr/bin/env python3
"""
Calibration tool for ADS Aimbot
Helps find optimal settings for your system
"""

import json
import os
from termcolor import colored

def calibrate_settings():
    """Interactive calibration wizard"""
    print(colored("\n🎯 ADS AIMBOT CALIBRATION WIZARD", "cyan", attrs=["bold"]))
    print("="*60)
    
    settings = {}
    
    # FOV Calibration
    print("\n1. FIELD OF VIEW (FOV)")
    print("   Larger = sees more, slower performance")
    print("   Smaller = faster, but limited view")
    
    while True:
        try:
            fov = int(input("   Enter FOV size (250-500, default 350): ") or "350")
            if 100 <= fov <= 1000:
                settings['fov'] = fov
                break
            else:
                print("   Please enter value between 100-1000")
        except ValueError:
            print("   Please enter a valid number")
    
    # Smoothness Calibration
    print("\n2. SMOOTHNESS")
    print("   Lower = smoother but slower")
    print("   Higher = faster but choppier")
    
    options = [
        (0.05, "Very Smooth - Slow tracking"),
        (0.10, "Smooth - Good for sniping"),
        (0.15, "Balanced - Recommended"),
        (0.20, "Responsive - Good for close combat"),
        (0.30, "Fast - May be choppy")
    ]
    
    print("\n   Options:")
    for i, (value, desc) in enumerate(options, 1):
        print(f"   {i}. {value:.2f} - {desc}")
    
    while True:
        try:
            choice = input(f"   Choose (1-{len(options)}, default 3): ") or "3"
            choice = int(choice) - 1
            if 0 <= choice < len(options):
                settings['smooth_factor'] = options[choice][0]
                break
            else:
                print(f"   Please enter 1-{len(options)}")
        except ValueError:
            print("   Please enter a valid number")
    
    # Confidence Calibration
    print("\n3. DETECTION CONFIDENCE")
    print("   Higher = more accurate, fewer detections")
    print("   Lower = more detections, more false positives")
    
    while True:
        try:
            conf = float(input("   Enter confidence (0.1-0.9, default 0.45): ") or "0.45")
            if 0.1 <= conf <= 0.9:
                settings['confidence'] = conf
                break
            else:
                print("   Please enter value between 0.1-0.9")
        except ValueError:
            print("   Please enter a valid number")
    
    # Humanization
    print("\n4. HUMANIZATION")
    print("   Adds random noise to appear more human")
    
    humanize = input("   Enable humanization? (y/n, default y): ") or "y"
    settings['humanization'] = humanize.lower() == 'y'
    
    if settings['humanization']:
        noise = float(input("   Noise intensity (0.5-3.0, default 1.5): ") or "1.5")
        settings['noise_intensity'] = max(0.0, min(5.0, noise))
    
    # Save calibration
    config_path = os.path.join("lib", "config", "config.json")
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Update with calibrated values
        config['detection']['fov'] = settings['fov']
        config['detection']['confidence'] = settings['confidence']
        config['aim']['smooth_factor'] = settings['smooth_factor']
        config['aim']['use_humanization'] = settings['humanization']
        
        if settings['humanization']:
            config['aim']['noise_intensity'] = settings.get('noise_intensity', 1.5)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        print(colored("\n✅ Calibration saved to config.json", "green"))
        
        # Display summary
        print("\n📊 CALIBRATION SUMMARY:")
        print("="*40)
        for key, value in settings.items():
            if key != 'humanization' or value:
                print(f"  {key.replace('_', ' ').title()}: {value}")
    
    return settings

if __name__ == "__main__":
    try:
        calibrate_settings()
        print(colored("\nCalibration complete! Run 'python lunar.py' to test.", "green", attrs=["bold"]))
    except KeyboardInterrupt:
        print(colored("\n\nCalibration cancelled", "yellow"))
    except Exception as e:
        print(colored(f"\n❌ Error: {e}", "red"))