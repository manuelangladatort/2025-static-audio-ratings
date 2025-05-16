import random
import json
from markupsafe import Markup

import psynet.experiment
from psynet.modular_page import AudioPrompt, ModularPage, PushButtonControl, NullControl, SurveyJSControl
from psynet.page import InfoPage
from psynet.timeline import Timeline, Event, ProgressDisplay, ProgressStage, FailedValidation
from psynet.trial import compile_nodes_from_directory
from psynet.trial.static import StaticNode, StaticTrial, StaticTrialMaker
from psynet.utils import get_logger
from psynet.prescreen import AntiphaseHeadphoneTest

from .instructions import welcome, welcome_soniclogos, requirements_headphones, instructions, instructions_soniclogos
from .questionnaire import questionnaire, questionnaire_soniclogos
from .goldsmiths_consent import GoldsmithsConsent

logger = get_logger()

########################################################################################################################
# Global parameters
########################################################################################################################

DEBUG = False
RECRUITER = "prolific"


if DEBUG:
    INITIAL_RECRUITMENT_SIZE = 10 
    NUM_TRIALS_PER_PARTICIPANT = 10
    N_REPEAT_TRIALS = 2
else:
    INITIAL_RECRUITMENT_SIZE = 10
    NUM_TRIALS_PER_PARTICIPANT = 30
    N_REPEAT_TRIALS = 5

TIME_ESTIMATE_RATING_TRIAL = 15
N_RATINGS_PER_TRIAL = 2

# Prolific parameters
def get_prolific_settings():
    with open("qualification_prolific_en.json", "r") as f:
        qualification = json.dumps(json.load(f))
    return {
        "recruiter": RECRUITER, 
        "prolific_estimated_completion_minutes": 12,
        "prolific_recruitment_config": qualification,
        "base_payment": 1.75,
        "auto_recruit": True,
        "currency": "£",
        "wage_per_hour": 0.01,
        "prolific_is_custom_screening": False # workaround to avoid the default screening question for psynet v11.9
    }


# rating scales
RATING_RESPONSE = [
    {"value": "1", "text": "1"},
    {"value": "2", "text": "2"},
    {"value": "3", "text": "3"},
    {"value": "4", "text": "4"},
    {"value": "5", "text": "5"},
    {"value": "6", "text": "6"},
    {"value": "7", "text": "7"}
    ]

MELODY_DURATION = 5

################################################################################
# Create nodes from s3 bucket
################################################################################    
# example path:
# https://2025-ising-natural-imitation.s3.eu-west-2.amazonaws.com/emotion-v1_network_100__degree_1__node_1435__stimulus.wav


# Names for emotion transmission project
# S3_BUCKET = "2025-ising-natural-imitation"
# S3_REGION = "eu-west-2"
# STIMULI_FILENAME = "stimuli-2025-emotion-transmission.txt" 

# Names for sonic logos project
S3_BUCKET = "2025-audio-logos"
S3_REGION = "eu-central-1"
STIMULI_FILENAME = "stimuli-sonic-logos.txt" # list of stimuli names for sonic logos project


def get_s3_url(stimulus):
    return f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{stimulus}"

with open(STIMULI_FILENAME, "r") as f:
    stimuli = f.read().splitlines()

nodes = [
    StaticNode(
        definition={"url": get_s3_url(stimulus)},
    )
    for stimulus in stimuli
]


################################################################################
# AntiphaseHeadphoneTest
################################################################################

# add fail logic in AntiphaseHeadphoneTest
class AntiphaseHeadphoneTestFailLogic(AntiphaseHeadphoneTest):

    def check_fail_logic(self):

        return ModularPage(
            "fail_headphone_test",
            prompt=Markup(
                f"""
                Unfortunately we encountered technical problems and you cannot proceed with the study.<br><br>
                <b><b>Please return the study.</b></b><br><br>
                We hope you can participate in our studies in the future.
                """
            ),
            control=NullControl(show_next_button=False),
            time_estimate=5,
        )

################################################################################
# Rating Trial
################################################################################    
class MULTIPLE_RATING_TRIAL_AUDIO(ModularPage):
    def __init__(self, node, show_current_trial, rating_response):
        super().__init__(
            "audio_multiple_rating",
            AudioPrompt(
                node.definition["url"],
                Markup(
                    f"""
                    <h3>Listen to the melody and evaluate it</h3>
                    <hr>
                    Please rate the melodies based on the quality of the music, not on the quality of the voice or the recording.
                    {show_current_trial}
                    <hr>
                    """
                ),
                controls=False,
            ),
            SurveyJSControl(
                    {
                        "logoPosition": "right",
                        "pages": [
                            {
                                "name": "ratings_melody",
                                "elements": [
                                    {
                                        "type": "rating",
                                        "name": "liking",
                                        "title": "How much do you like the melody?",
                                        "rateValues": rating_response,
                                        "minRateDescription": "Not at all",
                                        "maxRateDescription": "Very much",
                                    },
                                    {
                                        "type": "rating",
                                        "name": "emotionality",
                                        "title": "How emotional is the melody?",
                                        "rateValues": rating_response,
                                        "minRateDescription": "Not at all",
                                        "maxRateDescription": "Very much",
                                    },
                                    {
                                        "type": "rating",
                                        "name": "valence",
                                        "title": "How positive or negative is the emotion expressed in the melody?",
                                        "rateValues": rating_response,
                                        "minRateDescription": "Very negative",
                                        "maxRateDescription": "Very positive",
                                    },
                                    {
                                        "type": "rating",
                                        "name": "arousal",
                                        "title": "What level of energy or activation is expressed in the melody?",
                                        "rateValues": rating_response,
                                        "minRateDescription": "Very calm",
                                        "maxRateDescription": "Very energetic",
                                    },
                                ],
                            },
                        ],
                    },
                ),
            events={
                "promptStart": Event(is_triggered_by="trialStart", delay=1),
                "responseEnable": Event(is_triggered_by="promptEnd", delay=1),
                "submitEnable": Event(is_triggered_by="promptEnd", delay=1),
                },
            bot_response=lambda: {"rating": "3",},
        )

    def validate(self, response, **kwargs):
        # Check if all required fields are present
        required_fields = ["liking", "emotionality", "valence", "arousal"]
        provided_responses = 0
        
        for field in required_fields:
            if field in response.answer and response.answer[field]:
                provided_responses += 1
        
        if provided_responses < 4:
            return FailedValidation("Please answer all the questions")
        
        return None
    

class MULTIPLE_RATING_TRIAL_AUDIOLOGO(ModularPage):
    def __init__(self, node, show_current_trial, rating_response):
        super().__init__(
            "audio_multiple_rating",
            AudioPrompt(
                node.definition["url"],
                Markup(
                    f"""
                    <h3>Listen to the melody and evaluate it</h3>
                    <hr>
                    Please rate the melody as accurately as possible.
                    {show_current_trial}
                    <hr>
                    """
                ),
                controls=False,
            ),
            SurveyJSControl(
                    {
                        "logoPosition": "right",
                        "pages": [
                            {
                                "name": "ratings_melody",
                                "elements": [
                                    {
                                        "type": "rating",
                                        "name": "liking",
                                        "title": "How much do you like the melody?",
                                        "rateValues": rating_response,
                                        "minRateDescription": "Not at all",
                                        "maxRateDescription": "Very much",
                                    },
                                    {
                                        "type": "rating",
                                        "name": "memorability",
                                        "title": "How memorable is the melody?",
                                        "rateValues": rating_response,
                                        "minRateDescription": "Not at all",
                                        "maxRateDescription": "Very much",
                                    },
                                    {
                                        "type": "rating",
                                        "name": "emotionality",
                                        "title": "How emotional is the melody?",
                                        "rateValues": rating_response,
                                        "minRateDescription": "Not at all",
                                        "maxRateDescription": "Very much",
                                    },
                                    {
                                        "type": "rating",
                                        "name": "familiarity",
                                        "title": "How familiar is the melody?",
                                        "rateValues": rating_response,
                                        "minRateDescription": "Not at all",
                                        "maxRateDescription": "Very much",
                                    },
                                ],
                            },
                        ],
                    },
                ),
            events={
                "promptStart": Event(is_triggered_by="trialStart", delay=1),
                "responseEnable": Event(is_triggered_by="promptEnd", delay=1),
                "submitEnable": Event(is_triggered_by="promptEnd", delay=1),
                },
            bot_response=lambda: {"rating": "3",},
        )

    def validate(self, response, **kwargs):
        # Check if all required fields are present
        required_fields = ["liking", "memorability", "emotionality", "familiarity"]
        provided_responses = 0
        
        for field in required_fields:
            if field in response.answer and response.answer[field]:
                provided_responses += 1
        
        if provided_responses < 4:
            return FailedValidation("Please answer all the questions")
        
        return None


class AudioRatingTrial(StaticTrial):
    time_estimate = 5

    def show_trial(self, experiment, participant):
        return ModularPage(
            "audio_rating",
            AudioPrompt(
                self.node.definition["url"],
                "How much do you like this sung melody?",
            ),
            PushButtonControl(
                ["Not at all", "A little", "Very much"],
            ),
        )
    
class AudioMultipleRatingTrial(StaticTrial):
    time_estimate = TIME_ESTIMATE_RATING_TRIAL

    def show_trial(self, experiment, participant):

        current_trial = self.position + 1
        total_num_trials = NUM_TRIALS_PER_PARTICIPANT + N_REPEAT_TRIALS
        show_current_trial = f'<br><br>Trial number {current_trial} out of {total_num_trials} possible maximum trials.'


        # return MULTIPLE_RATING_TRIAL_AUDIO(self.node, show_current_trial, RATING_RESPONSE)
        return MULTIPLE_RATING_TRIAL_AUDIOLOGO(self.node, show_current_trial, RATING_RESPONSE)


class Exp(psynet.experiment.Experiment):
    label = "Static audio logo rating experiment"

    config = {
        **get_prolific_settings(),
        "initial_recruitment_size": INITIAL_RECRUITMENT_SIZE,
        "title": "Experiment on Musical Melodies (Chrome browser, ~12 mins)",
        "description": "In this experiment you will listen to musical melodies and asked to evaluate them on different dimensions.",
        "contact_email_on_error": "m.angladatort@gold.ac.uk",
        "organization_name": "Goldsmiths, University of London",
        # "docker_image_base_name": "docker.io/manuelangladatort/iterated-singing",
        "show_reward": False
    }

    timeline = Timeline(
        GoldsmithsConsent(),
        # welcome(),
        welcome_soniclogos(),
        requirements_headphones(),
        # AntiphaseHeadphoneTestFailLogic(),
        InfoPage("Well done! You can now start with the experiment.", time_estimate=2),
        # instructions(),
        instructions_soniclogos(),
        StaticTrialMaker(
            id_="audio_rating_experiment",
            trial_class=AudioMultipleRatingTrial,
            nodes=nodes,
            target_n_participants=None,
            recruit_mode="n_trials",
            target_trials_per_node=N_RATINGS_PER_TRIAL,
            expected_trials_per_participant=NUM_TRIALS_PER_PARTICIPANT,
            max_trials_per_participant=NUM_TRIALS_PER_PARTICIPANT,
            n_repeat_trials=N_REPEAT_TRIALS,
            fail_trials_on_premature_exit=True,
            fail_trials_on_participant_performance_check=False,
            allow_repeated_nodes=False,
        ),
        # questionnaire(),
        questionnaire_soniclogos()
    )
