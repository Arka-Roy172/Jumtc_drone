# import asyncio
# import json
# import sys
# import random
# import websockets
# import time
# from typing import Dict, Any, Optional
# from drone_simulator.logging_config import get_logger

# logger = get_logger("client")

# class DroneClient:
#     """WebSocket client for testing the drone simulator."""
    
#     def __init__(self, uri: str = "ws://localhost:8765"):
#         """Initialize the client."""
#         self.uri = uri
#         self.connection_id = None
#         self.telemetry = None
#         self.metrics = None
#         self.start_time = time.time()
#         self.command_count = 0
#         logger.info(f"Drone client initialized with server URI: {uri}")
    
#     async def connect(self) -> None:
#         """Connect to the WebSocket server and immediately start autonomous operation."""
#         logger.info(f"Attempting to connect to {self.uri}")
#         print(f"Connecting to {self.uri} and starting autonomous mode...")
        
#         try:
#             # Configure ping_interval and ping_timeout properly
#             logger.debug("Establishing WebSocket connection")
#             async with websockets.connect(
#                 self.uri, 
#                 ping_interval=20,  # Send ping every 20 seconds
#                 ping_timeout=10,   # Wait 10 seconds for pong response
#                 close_timeout=5    # Wait 5 seconds for close to complete
#             ) as websocket:
#                 # Receive welcome message
#                 response = await websocket.recv()
#                 data = json.loads(response)
#                 self.connection_id = data.get("connection_id")
#                 logger.info(f"Connected successfully with ID: {self.connection_id}")
#                 logger.info(f"Server message: {data['message']}")
#                 print(f"Connected with ID: {self.connection_id}")
#                 print(f"Server says: {data['message']}")
                
#                 # Immediately start autonomous operation
#                 await self._autonomous_operation(websocket)
                
#         except websockets.exceptions.ConnectionClosedError as e:
#             logger.error(f"Connection closed abnormally: {e}")
#             print("\nThe connection was closed unexpectedly. Possible reasons:")
#             print("- Server crashed or restarted")
#             print("- Network issues causing ping timeout")
#             print("- Server closed the connection due to inactivity")
            
#         except websockets.exceptions.ConnectionClosedOK:
#             logger.info("Connection closed normally by the server")
            
#         except ConnectionRefusedError:
#             logger.error(f"Connection refused. Is the server running at {self.uri}?")
#             print("\nTroubleshooting steps:")
#             print("1. Make sure the server is running: python run_server.py")
#             print("2. Check if the server is listening on the correct address")
#             print("3. Check if there are any firewalls blocking the connection")
#             print("4. Try 'ws://127.0.0.1:8765' instead of 'ws://localhost:8765'")
            
#         except Exception as e:
#             logger.error(f"Connection error: {e}", exc_info=True)
#             print(f"\nConnection error: {e}")
        
#         finally:
#             # Log session summary
#             session_duration = time.time() - self.start_time
#             logger.info(f"Session summary - "
#                       f"Duration: {session_duration:.1f}s, "
#                       f"Commands sent: {self.command_count}, "
#                       f"Connection ID: {self.connection_id}")
    
#     async def send_command(self, websocket, speed: int, altitude: int, movement: str) -> Optional[Dict[str, Any]]:
#         """Send a command to the drone server and return the response."""
#         try:
#             data = {
#                 "speed": speed,
#                 "altitude": altitude,
#                 "movement": movement
#             }
#             self.command_count += 1
#             logger.info(f"Sending command #{self.command_count}: {data}")
            
#             await websocket.send(json.dumps(data))
            
#             response = await websocket.recv()
#             response_data = json.loads(response)
            
#             # Check if the drone has crashed
#             if response_data.get("status") == "crashed":
#                 crash_message = response_data.get('message', 'Unknown crash')
#                 logger.warning(f"Drone crashed: {crash_message}")
                
#                 print(f"\n*** DRONE CRASHED: {crash_message} ***")
#                 print("Connection will be terminated.")
                
#                 # Update metrics one last time
#                 if "metrics" in response_data:
#                     self.metrics = response_data["metrics"]
#                     logger.info(f"Final metrics: {self.metrics}")
                
#                 # Show final telemetry
#                 if "final_telemetry" in response_data:
#                     self.telemetry = response_data["final_telemetry"]
#                     logger.info(f"Final telemetry: {self.telemetry}")
#                     self.display_status()
                
#                 print("\nFinal Flight Statistics:")
#                 print(f"Total distance traveled: {self.metrics.get('total_distance', 0)}")
#                 print(f"Successful flight iterations: {self.metrics.get('iterations', 0)}")
#                 print("\nConnection terminated due to crash")
                
#                 # Return None to indicate a crash occurred
#                 return None
            
#             logger.debug(f"Received response: {response_data}")
#             return response_data
            
#         except websockets.exceptions.ConnectionClosed as e:
#             logger.error(f"Connection closed while sending command: {e}")
#             raise
            
#         except Exception as e:
#             logger.error(f"Error sending command: {e}", exc_info=True)
#             return None
    
#     async def interactive_control(self, websocket) -> None:
#         """Interactively control the drone through the console."""
#         logger.info("Starting interactive control")
        
#         print("\n==== Drone Simulator Interactive Console ====")
#         print("Commands: 'exit' to quit, 'help' for instructions, 'auto' for auto pilot")
#         print("Input format: speed,altitude,movement (e.g., '2,0,fwd')")
#         print("Keep-alive pings are sent automatically every 20 seconds")
        
#         help_text = """
# Commands:
# - speed: integer 0-5
# - altitude: positive or negative integer
# - movement: 'fwd' or 'rev'

# Examples:
# - 3,0,fwd   # Move forward at speed 3
# - 0,5,fwd   # Gain altitude by 5 units
# - 2,-1,rev  # Move backward and descend 1 unit
# - auto      # Start auto pilot mode
# - exit      # Exit the client
# - help      # Show this help message
# - status    # Show current telemetry and metrics
# - ping      # Send a keep-alive command (0,0,fwd)
#         """
        
#         try:
#             while True:
#                 command = input("\nEnter command: ")
#                 logger.debug(f"User entered command: {command}")
                
#                 if command.lower() == 'exit':
#                     logger.info("User requested exit")
#                     break
                    
#                 if command.lower() == 'help':
#                     print(help_text)
#                     continue
                
#                 if command.lower() == 'status' and self.telemetry:
#                     self.display_status()
#                     continue
                
#                 if command.lower() == 'auto':
#                     logger.info("Starting auto pilot mode")
#                     await self.auto_pilot(websocket)
#                     continue
                    
#                 if command.lower() == 'ping':
#                     print("Sending keep-alive ping...")
#                     logger.info("User requested ping")
#                     data = await self.send_command(websocket, 0, 0, "fwd")
#                     if data:
#                         self.update_state(data)
#                         print("Keep-alive successful")
#                     continue
                
#                 try:
#                     # Parse command
#                     parts = command.split(',')
#                     if len(parts) != 3:
#                         print("Invalid command format. Use: speed,altitude,movement")
#                         logger.warning(f"Invalid command format: {command}")
#                         continue
                        
#                     speed = int(parts[0])
#                     altitude = int(parts[1])
#                     movement = parts[2].strip()
                    
#                     # Send command
#                     data = await self.send_command(websocket, speed, altitude, movement)
#                     if data:
#                         self.update_state(data)
#                         self.display_status()
#                     elif data is None:  # Crash occurred
#                         break
                        
#                 except ValueError as e:
#                     print(f"Invalid input format: {e}")
#                     print("Use format: speed,altitude,movement (e.g., '2,0,fwd')")
#                     logger.warning(f"Invalid input format: {e}")
                
#         except KeyboardInterrupt:
#             logger.info("User interrupted the client with Ctrl+C")
#             print("\nExiting...")
            
#         except websockets.exceptions.ConnectionClosed:
#             logger.warning("Connection to server was closed")
#             print("\nConnection to server was closed")
    
#     async def auto_pilot(self, websocket) -> None:
#         """Run an automated test sequence."""
#         logger.info("Starting auto pilot sequence")
#         print("\n==== Auto Pilot Mode ====")
#         print("Press Ctrl+C to exit auto pilot")
        
#         try:
#             # Test sequence
#             actions = []

#             # Simulated crash logic thresholds
#             MAX_SPEED = 5
#             MIN_SPEED = 0
#             # Subject to change
#             telemetry = self.telemetry or {}
#             for _ in range(15):   # Generate 15 dynamic actions
#               # Use last telemetry from server
#               dust = self.telemetry.get("dust",0)
#               sand = self.telemetry.get("sand",0)
#               wind = self.telemetry.get("wind", 0)
#               gyro = self.telemetry.get("gyro", 0)
#               sensor = self.telemetry.get("sensor", "green")
#               battery = self.telemetry.get("battery", 100)
#               speed, altitude, movement = 2,0, "fwd"  # Defaults

#               if speed == MAX_SPEED and sensor == "yellow" and battery >= 50 and dust <= 90 and wind <= 80 :
#                  speed = MAX_SPEED
#                  altitude =  random.randint(0,1000)
#                  movement = "fwd"
#               elif sensor == "red" and (battery > 50 or battery <10) :
#                   speed = random.randint(0,3)
#                   altitude = random.randint(0,3)
#                   movement = "fwd"
#               elif dust > 90 or wind > 85 :
#                   speed = max(0, speed-1)
#                   altitude = max(0, altitude-1)
#                   movement = "fwd"
#               elif gyro > 45 :
#                   altitude = 0
#                   speed = 0
#                   movement = "fwd"

#               # Save actions to the list
#               actions.append((speed, altitude, movement)) 
            
#             for i, (speed, altitude, movement) in enumerate(actions, 1):
#                 try:
#                     logger.info(f"Auto pilot step {i}/{len(actions)}: "
#                               f"speed={speed}, altitude={altitude}, movement={movement}")
#                     print(f"\nAuto pilot step {i}/{len(actions)}")
#                     print(f"Sending command: speed={speed}, altitude={altitude}, movement={movement}")
                    
#                     data = await self.send_command(websocket, speed, altitude, movement)
#                     if data:
#                         self.update_state(data)
#                         self.display_status()
#                     else:
#                         logger.warning("Auto pilot aborted due to crash or error")
#                         print("Auto pilot aborted")
#                         return
                    
#                     await asyncio.sleep(1)  # Pause between commands
                    
#                 except Exception as e:
#                     print(f"Error during autopilot step {i}: {e}")
#                     break
                
#             logger.info("Auto pilot sequence completed successfully")
#             print("\nAuto pilot sequence completed")
            
#         except KeyboardInterrupt:
#             logger.info("Auto pilot stopped by user")
#             print("\nAuto pilot stopped")
            
#         except websockets.exceptions.ConnectionClosed:
#             logger.warning("Connection to server was closed during auto pilot")
#             print("\nConnection to server was closed")
    
#     def parse_telemetry(self, telemetry_data: Any) -> Optional[Dict[str, Any]]:
#         """Parse and validate telemetry data, handling different data types."""
#         if not telemetry_data:
#             logger.warning("Telemetry data is None or empty")
#             return None
        
#         if isinstance(telemetry_data, str):
#             try:
#                 telemetry = json.loads(telemetry_data)
#             except json.JSONDecodeError:
#                 logger.error(f"Invalid JSON format for telemetry data: {telemetry_data}")
#                 return None
#         elif isinstance(telemetry_data, dict):
#             telemetry = telemetry_data
#         else:
#             logger.error(f"Unexpected telemetry data type: {type(telemetry_data)}")
#             return None
        
#         # Validate telemetry data
#         if not all(key in telemetry for key in ["x_position", "y_position", "battery", "wind", "dust", "sensor", "gyro"]):
#             logger.error(f"Incomplete telemetry data: {telemetry}")
#             return None
        
#         return telemetry

#     def update_state(self, data: Dict[str, Any]) -> None:
#         """Update client state with server response."""
#         if data and data.get("status") == "success":
#             telemetry_data = data.get("telemetry")
#             telemetry = self.parse_telemetry(telemetry_data)

#             if telemetry:
#                 self.telemetry = telemetry
#                 self.metrics = data["metrics"]
#                 logger.debug(f"Updated state with telemetry: {self.telemetry}")
#                 logger.debug(f"Updated state with metrics: {self.metrics}")
#             else:
#                 logger.warning("Failed to parse telemetry data")
#         else:
#             error_message = data.get("message", "Unknown error") if data else "Empty response"
#             logger.warning(f"Error response: {error_message}")
#             print(f"\nError: {error_message}")
#             if data and "metrics" in data:
#                 self.metrics = data["metrics"]
    
#     def display_status(self) -> None:
#         """Display current telemetry and metrics."""
#         if not self.telemetry:
#             print("No telemetry data available yet")
#             return
        
#         print("\n----- Telemetry -----")
#         # print(f"Position: ({self.telemetry['x_position']}, {self.telemetry['y_position']})")
#         # print(f"Battery: {self.telemetry['battery']:.1f}%")
#         # print(f"Wind Speed: {self.telemetry['wind_speed']}%")
#         # print(f"Dust Level: {self.telemetry['dust_level']}%")
#         # print(f"Sensor Status: {self.telemetry['sensor_status']}")
#         # print(f"Gyroscope: {self.telemetry['gyroscope']}")
#         print(self.telemetry)
        
#         print("\n----- Metrics -----")
#         if self.metrics:
#             print(f"Successful Iterations: {self.metrics['iterations']}")
#             print(f"Total Distance: {self.metrics['total_distance']}")
#         else:
#             print("No metrics data available yet")
            
#     async def _autonomous_operation(self, websocket) -> None:
#         """Internal method for autonomous drone operation."""
#         logger.info("Starting autonomous operation")
#         print("\n==== Autonomous Operation Mode ====")
    
#         try:
#             iteration_count = 0
#             max_iterations = 1000  # Safety limit
            
#             # Initialize telemetry to avoid errors on first run
#             self.telemetry = {"x_position": 0, "y_position": 0, "battery": 100, "wind": 0, "dust": 0, "sensor": "green", "gyro": [0, 0, 0]}

#             while iteration_count < max_iterations:
#                 iteration_count += 1
            
#                 # Safely make autonomous decisions based on telemetry
#                 command = self._decide_next_action()  # Use internal decide function
            
#                 # Convert command to JSON string
#                 command_str = json.dumps(command)
            
#                 # Send command directly to WebSocket
#                 await websocket.send(command_str)
#                 self.command_count += 1
            
#                 # Receive and process response
#                 response = await websocket.recv()
            
#                 try:
#                     response_data = json.loads(response)
#                 except json.JSONDecodeError:
#                     logger.error(f"Failed to decode JSON response: {response}")
#                     print(f"\nError: Could not decode JSON response: {response}")
#                     break
            
#                 # Safely update state based on response
#                 if response_data.get("status") == "crashed":
#                     print(f"\n*** DRONE CRASHED: {response_data.get('message', 'Unknown crash')} ***")
#                     break
#                 elif response_data.get("status") == "success":
#                     # Safely update telemetry and metrics
#                     telemetry = response_data.get("telemetry")
#                     if telemetry:
#                         if isinstance(telemetry, dict):
#                             self.telemetry = telemetry
#                         else:
#                             logger.warning(f"Telemetry is not a dictionary: {type(telemetry)}")
#                             # Handle the case where telemetry is not a dictionary
#                             # For example, set it to an empty dictionary or use a default
#                             self.telemetry = {}
#                     metrics = response_data.get("metrics")
#                     if metrics:
#                         self.metrics = metrics
                
#                     # Safely display current status (optional)
#                     if isinstance(self.telemetry, dict):
#                         x_position = self.telemetry.get('x_position', 0)
#                         y_position = self.telemetry.get('y_position', 0)
#                         print(f"Iteration {iteration_count}: {command} -> {x_position}, {y_position}")
#                     else:
#                         logger.warning(f"Telemetry data is not a dictionary: {type(self.telemetry)}")
            
#                 # Add small delay between commands
#                 await asyncio.sleep(0.5)
            
#         except KeyboardInterrupt:
#             print("\nAutonomous operation stopped by user")
#         except Exception as e:
#             logger.error(f"Error during autonomous operation: {e}", exc_info=True)
#             print(f"\nError during autonomous operation: {e}")
            
#     def _decide_next_action(self) -> dict:
#         """Internal method to determine next drone action based on current telemetry."""
#         # Safely get default values if no telemetry yet
#         if not self.telemetry or not isinstance(self.telemetry, dict):
#             # If telemetry is not available or not a dictionary, return default values
#             return {"speed": 1, "altitude": 10, "movement": "fwd"}
        
#         # Safely extract current telemetry data
#         dust = self.telemetry.get("dust", 0)
#         sand = self.telemetry.get("sand", 0)
#         wind = self.telemetry.get("wind", 0)
#         gyro = self.telemetry.get("gyro", [0, 0, 0])
#         sensor = self.telemetry.get("sensor", "green")
#         battery = self.telemetry.get("battery", 100)
#         x_position = self.telemetry.get("x_position", 0)
#         y_position = self.telemetry.get("y_position", 0)
        
#         # Make decisions based on crash conditions
        
#         # 1. Handle sensor status altitude restrictions
#         if sensor == "red":
#             altitude = min(2, y_position if y_position >= 0 else 0)  # Stay below 3
#         elif sensor == "yellow":
#             altitude = min(900, y_position if y_position >= 0 else 0)  # Stay below 1000
#         else:  # GREEN sensor
#             # Higher altitude is more efficient for battery (0.6x drain)
#             altitude = min(4000, y_position + 100 if y_position >= 0 else 100)
        
#         # 2. Handle stability issues
#         if isinstance(gyro, list) and any(abs(g) > 40 for g in gyro):  # Approaching dangerous tilt
#             speed = max(1, self.telemetry.get("speed", 3) - 1)  # Slow down
#         elif dust > 80 or wind > 80:  # Environmental challenges
#             speed = 2  # Conservative speed
#         elif battery < 25:  # Low battery
#             speed = 1  # Conserve power
#         else:  # Normal conditions
#             speed = 3  # Moderate speed
        
#         # 3. Handle range limits
#         if abs(x_position) > 90000:  # Approaching range limit
#             movement = "rev" if x_position > 0 else "fwd"  # Turn around
#         else:
#             movement = "fwd"  # Normal forward movement
        
#         return {"speed": speed, "altitude": altitude, "movement": movement}
    

# def main() -> None:
#     """Start the drone client."""
#     # Parse command line arguments
#     if len(sys.argv) > 1:
#         uri = sys.argv[1]
#     else:
#         uri = "ws://localhost:8765"
    
#     logger.info(f"Starting Drone Client with server URI: {uri}")
    
#     client = DroneClient(uri)
#     try:
#         asyncio.run(client.connect())
#     except KeyboardInterrupt:
#         logger.info("Client stopped by user")
#         print("\nClient stopped by user")

# if __name__ == "__main__":
#     main()
