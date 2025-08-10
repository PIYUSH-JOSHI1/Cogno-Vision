from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from utils.file_manager import file_manager
import cv2
import numpy as np
import base64
import io
from PIL import Image
import json
import os
import math
import mediapipe as mp
import random

dyspraxia_bp = Blueprint('dyspraxia', __name__)

class DyspraxiaAI:
    def __init__(self):
        # Initialize MediaPipe for hand and pose detection
        self.mp_hands = mp.solutions.hands
        self.mp_pose = mp.solutions.pose
        self.mp_draw = mp.solutions.drawing_utils
        
        # Hand detection setup
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # Pose detection setup
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        self.balance_exercises = [
            {
                'name': 'Single Leg Stand',
                'description': 'Stand on one foot for the target duration',
                'instructions': 'Lift one foot off the ground and maintain balance. Use your arms for stability.',
                'duration': 15, 'difficulty': 'easy',
                'tips': ['Focus on a fixed point ahead', 'Keep your core engaged', 'Breathe normally'],
                'pose_requirements': {'single_leg': True, 'balance_threshold': 0.15}
            },
            {
                'name': 'Heel-to-Toe Walk',
                'description': 'Walk in a straight line placing heel directly in front of toe',
                'instructions': 'Walk forward in a straight line, placing your heel directly in front of your toe with each step.',
                'duration': 20, 'difficulty': 'medium',
                'tips': ['Look ahead, not down', 'Take your time', 'Keep arms out for balance'],
                'pose_requirements': {'walking_pattern': True, 'foot_alignment': True}
            },
            {
                'name': 'Balance Beam Walk',
                'description': 'Walk along an imaginary line maintaining balance',
                'instructions': 'Imagine a straight line on the floor and walk along it without stepping off.',
                'duration': 25, 'difficulty': 'medium',
                'tips': ['Start slowly', 'Use peripheral vision', 'Practice daily for improvement'],
                'pose_requirements': {'straight_line': True, 'balance_threshold': 0.2}
            },
            {
                'name': 'Eyes Closed Balance',
                'description': 'Balance on one foot with eyes closed',
                'instructions': 'Close your eyes and balance on one foot. This challenges your proprioception.',
                'duration': 12, 'difficulty': 'hard',
                'tips': ['Start with eyes open', 'Have someone nearby for safety', 'Focus on body awareness'],
                'pose_requirements': {'single_leg': True, 'balance_threshold': 0.1, 'eyes_closed': True}
            },
            {
                'name': 'Dynamic Balance',
                'description': 'Balance while moving your arms',
                'instructions': 'Stand on one foot while moving your arms in different directions.',
                'duration': 18, 'difficulty': 'hard',
                'tips': ['Start with small movements', 'Gradually increase range', 'Maintain core stability'],
                'pose_requirements': {'single_leg': True, 'arm_movement': True, 'balance_threshold': 0.12}
            },
            {
                'name': 'Tandem Stance',
                'description': 'Stand with one foot directly in front of the other, heel to toe.',
                'instructions': 'Place one foot directly in front of the other, heel touching toe, and hold your balance.',
                'duration': 15, 'difficulty': 'medium',
                'tips': ['Keep arms out for balance', 'Focus on a point ahead', 'Switch feet after each round'],
                'pose_requirements': {'tandem_stance': True, 'balance_threshold': 0.18}
            },
            {
                'name': 'Sideways Walk',
                'description': 'Walk sideways in a straight line maintaining balance.',
                'instructions': 'Take slow, controlled steps to the side, keeping your body upright.',
                'duration': 20, 'difficulty': 'easy',
                'tips': ['Move slowly', 'Keep feet close to the ground', 'Use arms for balance'],
                'pose_requirements': {'lateral_movement': True, 'balance_threshold': 0.25}
            },
            {
                'name': 'Balance with Object',
                'description': 'Balance on one foot while holding an object overhead.',
                'instructions': 'Stand on one foot and hold a lightweight object (like a book) above your head.',
                'duration': 12, 'difficulty': 'hard',
                'tips': ['Keep core tight', 'Focus on posture', 'Switch feet and hands'],
                'pose_requirements': {'single_leg': True, 'arms_raised': True, 'balance_threshold': 0.1}
            },
            {
                'name': 'March in Place',
                'description': 'March in place, lifting knees high and maintaining balance.',
                'instructions': 'Lift each knee high as you march in place, keeping your balance steady.',
                'duration': 25, 'difficulty': 'easy',
                'tips': ['March slowly', 'Keep back straight', 'Use arms for rhythm'],
                'pose_requirements': {'marching': True, 'knee_lift': True, 'balance_threshold': 0.3}
            },
            {
                'name': 'Tree Pose Hold',
                'description': 'Stand on one foot with the other foot placed on inner thigh.',
                'instructions': 'Place one foot on the inner thigh of standing leg, hands together at chest.',
                'duration': 20, 'difficulty': 'medium',
                'tips': ['Press foot into leg', 'Keep hips level', 'Focus on breathing'],
                'pose_requirements': {'tree_pose': True, 'balance_threshold': 0.12}
            },
            {
                'name': 'Clock Reaches',
                'description': 'Stand on one foot and reach arms to different clock positions.',
                'instructions': 'Standing on one foot, reach your arms to 12, 3, 6, and 9 o\'clock positions.',
                'duration': 30, 'difficulty': 'hard',
                'tips': ['Move slowly', 'Keep standing leg stable', 'Breathe throughout'],
                'pose_requirements': {'single_leg': True, 'directional_reach': True, 'balance_threshold': 0.1}
            },
            {
                'name': 'Weight Shift Balance',
                'description': 'Shift weight from side to side while maintaining balance.',
                'instructions': 'Stand with feet hip-width apart and slowly shift weight from left to right.',
                'duration': 25, 'difficulty': 'easy',
                'tips': ['Move slowly and controlled', 'Keep both feet on ground', 'Feel weight transfer'],
                'pose_requirements': {'weight_shift': True, 'balance_threshold': 0.2}
            },
            {
                'name': 'Stork Stand Progressive',
                'description': 'Progress from two feet to one foot balance with arm variations.',
                'instructions': 'Start two feet, then one foot, then add arm movements while balancing.',
                'duration': 35, 'difficulty': 'hard',
                'tips': ['Progress gradually', 'Use wall if needed', 'Build up slowly'],
                'pose_requirements': {'progressive_balance': True, 'balance_threshold': 0.08}
            }
        ]
        
        self.coordination_games = [
            {
                'name': 'Rock Paper Scissors', 'description': 'Play against computer using hand gestures',
                'instructions': 'Make rock, paper, or scissors gestures with your hand',
                'type': 'gesture_recognition', 'rounds': 5, 'age_group': '10-18',
                'skills': ['hand_coordination', 'reaction_time', 'decision_making']
            },
            {
                'name': 'Simon Says Gestures', 'description': 'Follow gesture commands in sequence',
                'instructions': 'Copy the gestures shown on screen in the correct order',
                'type': 'sequence_memory', 'rounds': 7, 'age_group': '10-18',
                'skills': ['memory', 'gesture_control', 'attention']
            },
            {
                'name': 'Target Pointing', 'description': 'Point at targets that appear on screen',
                'instructions': 'Point your finger at the colored targets as they appear',
                'type': 'precision_pointing', 'rounds': 10, 'age_group': '10-18',
                'skills': ['precision', 'hand_eye_coordination', 'focus']
            },
            {
                'name': 'Mirror Match', 'description': 'Mirror the movements shown on screen',
                'instructions': 'Copy body movements and hand gestures like looking in a mirror',
                'type': 'body_coordination', 'rounds': 6, 'age_group': '12-18',
                'skills': ['body_awareness', 'bilateral_coordination', 'spatial_processing']
            },
            {
                'name': 'Rhythm Clapping', 'description': 'Clap along to rhythmic patterns',
                'instructions': 'Listen and clap along with the rhythm patterns shown',
                'type': 'rhythm_coordination', 'rounds': 8, 'age_group': '10-16',
                'skills': ['timing', 'auditory_processing', 'motor_planning']
            },
            {
                'name': 'Color Touch', 'description': 'Touch the correct colored objects quickly',
                'instructions': 'Point to or touch the objects of the specified color',
                'type': 'visual_motor', 'rounds': 12, 'age_group': '10-15',
                'skills': ['color_recognition', 'speed', 'visual_tracking']
            },
            {
                'name': 'Pattern Follow', 'description': 'Follow complex hand movement patterns',
                'instructions': 'Copy the hand movement sequences shown step by step',
                'type': 'pattern_coordination', 'rounds': 5, 'age_group': '13-18',
                'skills': ['sequential_processing', 'fine_motor', 'working_memory']
            },
            {
                'name': 'Balance & Point', 'description': 'Point at targets while balancing on one foot',
                'instructions': 'Balance on one foot while pointing at moving targets',
                'type': 'dual_task', 'rounds': 8, 'age_group': '12-18',
                'skills': ['balance', 'multitasking', 'postural_control']
            }
        ]

    def detect_hand_landmarks(self, frame_bytes):
        """Detect hand landmarks using MediaPipe and return gesture and processed image."""
        try:
            nparr = np.frombuffer(base64.b64decode(frame_bytes), np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None: return None, 'none', None
            
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(img_rgb)
            img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR) # For drawing
            
            hand_landmarks_data = None
            gesture = 'none'
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(
                        img_bgr, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                        self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                        self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2)
                    )
                    hand_landmarks_data = [{'x': lm.x, 'y': lm.y, 'z': lm.z} for lm in hand_landmarks.landmark]
                    gesture = self.classify_hand_gesture(hand_landmarks_data)
                    break # Process first hand found
            
            return hand_landmarks_data, gesture, img_bgr
            
        except Exception as e:
            print(f"Error in hand detection: {e}")
            return None, 'none', None

    def classify_hand_gesture(self, landmarks):
        """Classify hand gesture from landmark positions."""
        if not landmarks or len(landmarks) < 21: return 'none'
        try:
            thumb_tip, thumb_ip = landmarks[4], landmarks[3]
            index_tip, index_pip = landmarks[8], landmarks[6]
            middle_tip, middle_pip = landmarks[12], landmarks[10]
            ring_tip, ring_pip = landmarks[16], landmarks[14]
            pinky_tip, pinky_pip = landmarks[20], landmarks[18]
            
            fingers_up = []
            # Thumb check (works for both hands)
            if landmarks[17]['x'] < landmarks[5]['x']: # Simple Right Hand check
                fingers_up.append(thumb_tip['x'] > thumb_ip['x'])
            else: # Left Hand
                fingers_up.append(thumb_tip['x'] < thumb_ip['x'])
            
            # Other four fingers
            fingers_up.append(index_tip['y'] < index_pip['y'])
            fingers_up.append(middle_tip['y'] < middle_pip['y'])
            fingers_up.append(ring_tip['y'] < ring_pip['y'])
            fingers_up.append(pinky_tip['y'] < pinky_pip['y'])
            
            total_fingers = sum(fingers_up)
            
            if total_fingers == 0: return 'rock'
            if total_fingers == 5: return 'paper'
            if total_fingers == 2 and fingers_up[1] and fingers_up[2]: return 'scissors'
            if total_fingers == 1 and fingers_up[1]: return 'point'
            if total_fingers == 1 and fingers_up[0]: return 'thumbs_up'
            if total_fingers >= 4: return 'wave'
            
            return 'open_palm'
        except Exception as e:
            print(f"Error classifying gesture: {e}")
            return 'none'

    def detect_pose_landmarks(self, frame_bytes):
        """Detect pose landmarks using MediaPipe."""
        try:
            nparr = np.frombuffer(base64.b64decode(frame_bytes), np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None: return None, None
            
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.pose.process(img_rgb)
            img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR) # For drawing
            
            pose_landmarks_data = None
            if results.pose_landmarks:
                self.mp_draw.draw_landmarks(
                    img_bgr, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2)
                )
                pose_landmarks_data = [{'x': lm.x, 'y': lm.y, 'z': lm.z, 'visibility': lm.visibility} for lm in results.pose_landmarks.landmark]
            
            return pose_landmarks_data, img_bgr
            
        except Exception as e:
            print(f"Error in pose detection: {e}")
            return None, None

    def analyze_balance_pose(self, pose_landmarks):
        """Analyze balance from pose landmarks."""
        if not pose_landmarks or len(pose_landmarks) < 33:
            return {'balance_score': 0, 'feedback': ['No pose detected']}
        try:
            left_hip, right_hip = pose_landmarks[23], pose_landmarks[24]
            left_ankle, right_ankle = pose_landmarks[27], pose_landmarks[28]
            left_shoulder, right_shoulder = pose_landmarks[11], pose_landmarks[12]
            
            center_x = (left_hip['x'] + right_hip['x']) / 2
            center_y = (left_hip['y'] + right_hip['y']) / 2
            
            hip_width = abs(left_hip['x'] - right_hip['x'])
            shoulder_level = abs(left_shoulder['y'] - right_shoulder['y'])
            
            balance_score = 100
            feedback = []
            
            if center_x < 0.3 or center_x > 0.7:
                balance_score -= 30; feedback.append("Try to stay more centered.")
            if shoulder_level > 0.05:
                balance_score -= 20; feedback.append("Keep your shoulders level.")
                
            balance_score = max(0, balance_score)
            if balance_score > 85 and not feedback: feedback.append("Excellent balance!")
            elif balance_score > 70 and not feedback: feedback.append("Good stability!")

            return {
                'balance_score': balance_score,
                'center_of_mass': {'x': center_x, 'y': center_y},
                'feedback': feedback if feedback else ["Keep holding steady."]
            }
        except Exception as e:
            print(f"Error analyzing balance: {e}")
            return {'balance_score': 0, 'feedback': ['Analysis error']}


    # Frame saving is disabled to reduce storage usage on deployment
    def save_correct_pose_frame(self, img, user_id, exercise_name, timer):
        """Frame saving disabled: only analyze in memory, do not write to disk."""
        return False, None

    def generate_balance_exercise(self, difficulty='easy'):
        """Generate a balance exercise based on difficulty."""
        exercises = [ex for ex in self.balance_exercises if ex['difficulty'] == difficulty]
        if not exercises: exercises = self.balance_exercises
        return random.choice(exercises)
    
    def evaluate_balance_performance(self, duration, stability_scores):
        """Evaluate balance performance."""
        if not stability_scores:
            return {'score': 0, 'feedback': 'No data recorded', 'improvement_tips': []}
        
        avg_stability = sum(stability_scores) / len(stability_scores)
        completion_rate = min(100, (duration / 10) * 100)  # Assuming 10s target
        overall_score = (avg_stability * 0.7) + (completion_rate * 0.3)
        
        tips = []
        if overall_score >= 85: feedback = "Outstanding performance!"; tips.append("Try more challenging exercises.")
        elif overall_score >= 70: feedback = "Great improvement!"; tips.append("Focus on holding positions longer.")
        elif overall_score >= 50: feedback = "Good effort, keep practicing."; tips.extend(["Practice daily for better results.", "Focus on core strength."])
        else: feedback = "Keep working at it!"; tips.extend(["Start with easier exercises.", "Consider working with a therapist."])
        
        return {
            'score': round(overall_score, 1), 'avg_stability': round(avg_stability, 1),
            'completion_rate': round(completion_rate, 1), 'feedback': [feedback],
            'improvement_tips': tips
        }

    def save_game_data(self, user_id, game_data):
        """Save game results to a CSV file."""
        try:
            os.makedirs('data/dyspraxia', exist_ok=True)
            fieldnames = ['user_id', 'game_type', 'score', 'total_rounds', 'accuracy', 'game_time', 'correct_attempts', 'total_attempts', 'difficulty', 'age_appropriate', 'skills_practiced', 'timestamp']
            csv_data = {
                'user_id': user_id, 'game_type': game_data.get('game_type', 'unknown'),
                'score': game_data.get('score', 0), 'total_rounds': game_data.get('total_rounds', 0),
                'accuracy': round(game_data.get('accuracy', 0), 1), 'game_time': game_data.get('game_time', 0),
                'correct_attempts': game_data.get('correct_attempts', 0),
                'total_attempts': game_data.get('total_attempts', 0),
                'difficulty': game_data.get('difficulty', 'unknown'), 'age_appropriate': 'yes',
                'skills_practiced': ','.join(game_data.get('skills', [])), 'timestamp': file_manager.get_timestamp()
            }
            file_manager.append_csv('data/dyspraxia/games.csv', csv_data, fieldnames)
            return True
        except Exception as e:
            print(f"Error saving game data: {e}")
            return False

dyspraxia_ai = DyspraxiaAI()

# --- Navigation Routes ---
@dyspraxia_bp.route('/')
def main():
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    return render_template('dyspraxia/main.html')

@dyspraxia_bp.route('/balance-training')
def balance_training():
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    return render_template('dyspraxia/balance_training.html')

@dyspraxia_bp.route('/coordination-games')
def coordination_games():
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    return render_template('dyspraxia/coordination_games.html')


# --- Camera Exercise Definitions ---
camera_exercises_list = [
    {
        'name': 'Arm Raise',
        'description': 'Raise both arms above your head and hold for 5 seconds.',
        'instructions': 'Stand straight, raise both arms overhead, and keep them straight.',
        'duration': 5,
        'difficulty': 'easy',
        'movement': 'arm_raise'
    },
    {
        'name': 'Side Step',
        'description': 'Step to the side and back, repeat for 10 seconds.',
        'instructions': 'Step to your right, then left, keeping your body upright.',
        'duration': 10,
        'difficulty': 'easy',
        'movement': 'side_step'
    },
    {
        'name': 'March in Place',
        'description': 'March in place, lifting knees high for 10 seconds.',
        'instructions': 'Lift each knee high as you march in place.',
        'duration': 10,
        'difficulty': 'easy',
        'movement': 'march_in_place'
    },
    {
        'name': 'Squat Hold',
        'description': 'Hold a squat position for 8 seconds.',
        'instructions': 'Bend your knees and lower your hips as if sitting, hold.',
        'duration': 8,
        'difficulty': 'medium',
        'movement': 'squat_hold'
    },
    {
        'name': 'Torso Twist',
        'description': 'Twist your torso left and right for 10 seconds.',
        'instructions': 'Stand straight, twist your upper body left and right.',
        'duration': 10,
        'difficulty': 'medium',
        'movement': 'torso_twist'
    },
    {
        'name': 'Jumping Jacks',
        'description': 'Do jumping jacks for 10 seconds.',
        'instructions': 'Jump with legs apart and arms overhead, then return.',
        'duration': 10,
        'difficulty': 'medium',
        'movement': 'jumping_jacks'
    },
    {
        'name': 'Heel Walk',
        'description': 'Walk on your heels for 8 seconds.',
        'instructions': 'Lift your toes and walk forward on your heels.',
        'duration': 8,
        'difficulty': 'hard',
        'movement': 'heel_walk'
    },
    {
        'name': 'Balance Reach',
        'description': 'Stand on one foot and reach forward for 6 seconds.',
        'instructions': 'Balance on one foot, reach forward with both hands.',
        'duration': 6,
        'difficulty': 'hard',
        'movement': 'balance_reach'
    }
]

@dyspraxia_bp.route('/camera-exercises')
def camera_exercises():
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    return render_template('dyspraxia/camera_exercises.html', exercises=camera_exercises_list)

# --- Camera Exercise API: Detect Movement ---
@dyspraxia_bp.route('/detect-movement', methods=['POST'])
def detect_movement():
    if 'user_id' not in session: return jsonify({'success': False, 'message': 'Not logged in'})
    data = request.get_json()
    frame_data = data.get('frame', '')
    movement_type = data.get('movement', '')
    if not frame_data or not movement_type:
        return jsonify({'success': False, 'message': 'Missing frame or movement type'})
    try:
        pose_landmarks, img = dyspraxia_ai.detect_pose_landmarks(frame_data)
        detected = False
        feedback = []
        if pose_landmarks:
            # Movement detection logic
            if movement_type == 'arm_raise':
                # Both wrists above shoulders
                left_wrist = pose_landmarks[15]
                right_wrist = pose_landmarks[16]
                left_shoulder = pose_landmarks[11]
                right_shoulder = pose_landmarks[12]
                if left_wrist['y'] < left_shoulder['y'] and right_wrist['y'] < right_shoulder['y']:
                    detected = True
                    feedback.append('Arms raised correctly!')
                else:
                    feedback.append('Raise both arms above your head.')
            elif movement_type == 'side_step':
                # Detect lateral movement by ankle x distance
                left_ankle = pose_landmarks[27]
                right_ankle = pose_landmarks[28]
                if abs(left_ankle['x'] - right_ankle['x']) > 0.35:
                    detected = True
                    feedback.append('Good side step!')
                else:
                    feedback.append('Step wider to the side.')
            elif movement_type == 'march_in_place':
                # At least one knee above hip
                left_knee = pose_landmarks[25]
                right_knee = pose_landmarks[26]
                left_hip = pose_landmarks[23]
                right_hip = pose_landmarks[24]
                if left_knee['y'] < left_hip['y'] or right_knee['y'] < right_hip['y']:
                    detected = True
                    feedback.append('Great knee lift!')
                else:
                    feedback.append('Lift your knees higher.')
            elif movement_type == 'squat_hold':
                # Hip below knee
                left_hip = pose_landmarks[23]
                right_hip = pose_landmarks[24]
                left_knee = pose_landmarks[25]
                right_knee = pose_landmarks[26]
                if left_hip['y'] > left_knee['y'] and right_hip['y'] > right_knee['y']:
                    detected = True
                    feedback.append('Squat position held!')
                else:
                    feedback.append('Lower your hips more.')
            elif movement_type == 'torso_twist':
                # Shoulders rotated (difference in x)
                left_shoulder = pose_landmarks[11]
                right_shoulder = pose_landmarks[12]
                if abs(left_shoulder['x'] - right_shoulder['x']) > 0.25:
                    detected = True
                    feedback.append('Good torso twist!')
                else:
                    feedback.append('Twist your torso more.')
            elif movement_type == 'jumping_jacks':
                # Wrists above head and ankles apart
                left_wrist = pose_landmarks[15]
                right_wrist = pose_landmarks[16]
                left_ankle = pose_landmarks[27]
                right_ankle = pose_landmarks[28]
                head = pose_landmarks[0]
                if left_wrist['y'] < head['y'] and right_wrist['y'] < head['y'] and abs(left_ankle['x'] - right_ankle['x']) > 0.4:
                    detected = True
                    feedback.append('Jumping jack detected!')
                else:
                    feedback.append('Jump higher and spread your feet.')
            elif movement_type == 'heel_walk':
                # Toes above heels (simulate by ankle/foot landmarks)
                left_heel = pose_landmarks[29]
                right_heel = pose_landmarks[30]
                left_foot_index = pose_landmarks[31]
                right_foot_index = pose_landmarks[32]
                if left_foot_index['y'] < left_heel['y'] and right_foot_index['y'] < right_heel['y']:
                    detected = True
                    feedback.append('Heel walk detected!')
                else:
                    feedback.append('Lift your toes up for heel walk.')
            elif movement_type == 'balance_reach':
                # One foot on ground, both hands forward (wrists in front of hips)
                left_ankle = pose_landmarks[27]
                right_ankle = pose_landmarks[28]
                left_wrist = pose_landmarks[15]
                right_wrist = pose_landmarks[16]
                left_hip = pose_landmarks[23]
                right_hip = pose_landmarks[24]
                if (left_wrist['y'] < left_hip['y'] and right_wrist['y'] < right_hip['y']) and (abs(left_ankle['y'] - right_ankle['y']) > 0.2):
                    detected = True
                    feedback.append('Balance reach detected!')
                else:
                    feedback.append('Reach forward and balance on one foot.')
            else:
                feedback.append('Unknown movement type.')
        else:
            feedback.append('No pose detected.')
        return jsonify({'success': True, 'detected': detected, 'feedback': feedback})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error detecting movement: {str(e)}'}), 500

# --- Camera Exercise API: Save Result ---
@dyspraxia_bp.route('/save-camera-exercise', methods=['POST'])
def save_camera_exercise():
    if 'user_id' not in session: return jsonify({'success': False, 'message': 'Not logged in'})
    data = request.get_json()
    try:
        result_data = {
            'user_id': session['user_id'],
            'activity': 'camera_exercise',
            'exercise_name': data.get('exercise_name', ''),
            'duration': round(data.get('duration', 0), 2),
            'success': data.get('success', False),
            'timestamp': file_manager.get_timestamp()
        }
        fieldnames = ['user_id', 'activity', 'exercise_name', 'duration', 'success', 'timestamp']
        file_manager.append_csv('data/dyspraxia/progress.csv', result_data, fieldnames)
        return jsonify({'success': True, 'message': 'Camera exercise result saved'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error saving result: {str(e)}'}), 500

# --- Balance Training API Routes ---
@dyspraxia_bp.route('/process-frame', methods=['POST'])
def process_frame():
    """Process frame for balance exercises using MediaPipe."""
    if 'user_id' not in session: return jsonify({'success': False, 'message': 'Not logged in'})
    data = request.get_json()
    frame_data = data.get('frame', ''); exercise_name = data.get('exercise_name', ''); timer = data.get('timer', 0)
    if not frame_data or not exercise_name: return jsonify({'success': False, 'message': 'Missing frame or exercise name'})
    
    try:
        pose_landmarks, img = dyspraxia_ai.detect_pose_landmarks(frame_data)
        pose_correct, balance_score, feedback = False, 0, ["No pose detected."]

        if pose_landmarks:
            analysis = dyspraxia_ai.analyze_balance_pose(pose_landmarks)
            balance_score, feedback = analysis.get('balance_score', 0), analysis.get('feedback', [])
            if balance_score > 70: pose_correct = True
        
        # Frame saving disabled: do not write to disk
        frame_saved, saved_path = False, None
        # if pose_correct and img is not None:
        #     frame_saved, saved_path = dyspraxia_ai.save_correct_pose_frame(img, session['user_id'], exercise_name, timer)
        return jsonify({
            'success': True, 'pose_correct': pose_correct, 'balance_score': balance_score,
            'feedback': feedback, 'frame_saved': frame_saved, 'saved_path': saved_path,
            'autoend': timer <= 0, 'timer': timer
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error processing frame: {str(e)}'}), 500

@dyspraxia_bp.route('/get-balance-exercise', methods=['POST'])
def get_balance_exercise():
    if 'user_id' not in session: return jsonify({'success': False, 'message': 'Not logged in'})
    difficulty = request.get_json().get('difficulty', 'easy')
    try:
        exercise = dyspraxia_ai.generate_balance_exercise(difficulty)
        return jsonify({'success': True, 'exercise': exercise})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error generating exercise: {str(e)}'}), 500

@dyspraxia_bp.route('/submit-balance-result', methods=['POST'])
def submit_balance_result():
    if 'user_id' not in session: return jsonify({'success': False, 'message': 'Not logged in'})
    data = request.get_json()
    try:
        progress_data = {
            'user_id': session['user_id'], 'activity': 'balance_training',
            'exercise_name': data.get('exercise_name', ''), 'duration': round(data.get('duration', 0), 3),
            'stability_score': round(data.get('stability', 0), 0), 'timestamp': file_manager.get_timestamp()
        }
        fieldnames = ['user_id', 'activity', 'exercise_name', 'duration', 'stability_score', 'timestamp']
        file_manager.append_csv('data/dyspraxia/progress.csv', progress_data, fieldnames)
        return jsonify({'success': True, 'message': 'Progress saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error saving progress: {str(e)}'}), 500

# --- Coordination Games API Routes ---
@dyspraxia_bp.route('/detect-hand-gesture', methods=['POST'])
def detect_hand_gesture():
    if 'user_id' not in session: return jsonify({'success': False, 'message': 'Not logged in'})
    frame_data = request.get_json().get('frame', '')
    if not frame_data: return jsonify({'success': False, 'message': 'No frame data'})
    try:
        hand_landmarks, gesture, processed_img = dyspraxia_ai.detect_hand_landmarks(frame_data)
        processed_frame = None
        if processed_img is not None:
            _, buffer = cv2.imencode('.jpg', processed_img); processed_frame = base64.b64encode(buffer).decode('utf-8')
        return jsonify({
            'success': True, 'gesture': gesture, 'hand_detected': hand_landmarks is not None,
            'landmarks': hand_landmarks, 'processed_frame': processed_frame
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error detecting gesture: {str(e)}'}), 500

@dyspraxia_bp.route('/detect-pose', methods=['POST'])
def detect_pose():
    if 'user_id' not in session: return jsonify({'success': False, 'message': 'Not logged in'})
    frame_data = request.get_json().get('frame', '')
    if not frame_data: return jsonify({'success': False, 'message': 'No frame data'})
    try:
        pose_landmarks, processed_img = dyspraxia_ai.detect_pose_landmarks(frame_data)
        balance_analysis = dyspraxia_ai.analyze_balance_pose(pose_landmarks) if pose_landmarks else None
        processed_frame = None
        if processed_img is not None:
            _, buffer = cv2.imencode('.jpg', processed_img); processed_frame = base64.b64encode(buffer).decode('utf-8')
        return jsonify({
            'success': True, 'pose_detected': pose_landmarks is not None, 'pose_landmarks': pose_landmarks,
            'balance_analysis': balance_analysis, 'processed_frame': processed_frame
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error detecting pose: {str(e)}'}), 500

@dyspraxia_bp.route('/save-game-results', methods=['POST'])
def save_game_results():
    if 'user_id' not in session: return jsonify({'success': False, 'message': 'Not logged in'})
    data = request.get_json()
    try:
        game_type = data.get('game_type', '')
        game_info = next((g for g in dyspraxia_ai.coordination_games if g['name'] == game_type), None)
        game_data = { **data, 'skills': game_info['skills'] if game_info else [] }
        if dyspraxia_ai.save_game_data(session['user_id'], game_data):
            return jsonify({'success': True, 'message': 'Game results saved successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to save game results'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error saving game results: {str(e)}'}), 500

@dyspraxia_bp.route('/get-game-stats', methods=['GET'])
def get_game_stats():
    if 'user_id' not in session: return jsonify({'success': False, 'message': 'Not logged in'})
    try:
        user_games = [g for g in file_manager.read_csv('data/dyspraxia/games.csv') if g.get('user_id') == session['user_id']]
        if not user_games: raise FileNotFoundError
        total_games = len(user_games)
        game_counts = {}
        for game in user_games: game_counts[game.get('game_type')] = game_counts.get(game.get('game_type'), 0) + 1
        stats = {
            'total_games': total_games,
            'average_accuracy': round(sum(float(g.get('accuracy', 0)) for g in user_games) / total_games, 1),
            'total_time_played': round(sum(float(g.get('game_time', 0)) for g in user_games)),
            'favorite_game': max(game_counts.items(), key=lambda item: item[1])[0],
            'game_breakdown': game_counts,
            'recent_scores': [float(g.get('accuracy', 0)) for g in user_games[-5:]]
        }
        return jsonify({'success': True, 'stats': stats})
    except (FileNotFoundError, IndexError):
        return jsonify({'success': True, 'stats': {'total_games': 0, 'average_accuracy': 0, 'total_time_played': 0, 'favorite_game': 'N/A', 'game_breakdown': {}, 'recent_scores': []}})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error getting stats: {str(e)}'}), 500

@dyspraxia_bp.route('/validate-gesture', methods=['POST'])
def validate_gesture():
    if 'user_id' not in session: return jsonify({'success': False, 'message': 'Not logged in'})
    data = request.get_json(); frame_data = data.get('frame', ''); expected_gesture = data.get('expected_gesture', '')
    try:
        hand_landmarks, detected_gesture, processed_img = dyspraxia_ai.detect_hand_landmarks(frame_data)
        processed_frame = None
        if processed_img is not None:
            _, buffer = cv2.imencode('.jpg', processed_img); processed_frame = base64.b64encode(buffer).decode('utf-8')
        return jsonify({
            'success': True, 'detected_gesture': detected_gesture, 'expected_gesture': expected_gesture,
            'is_correct': detected_gesture == expected_gesture, 'hand_detected': hand_landmarks is not None,
            'processed_frame': processed_frame
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error validating gesture: {str(e)}'}), 500