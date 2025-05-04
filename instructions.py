from markupsafe import Markup
from psynet.page import InfoPage


def welcome():
    return InfoPage(
        Markup(
            """
            <h3>Thank you for taking part in this study</h3>
            <hr>
            We aim to study how emotions are perceived in music.<br><br>
            In the study, you will hear melodies sung by other people and asked to rate them using different rating scales.
            <hr>
            """
        ),
        time_estimate=3
    )


def requirements_headphones():
    return InfoPage(
        Markup(
            """
            <h3>Requirements</h3>
            <hr>
            <ul>
                <li>You must use headphones or earphones to listen to the melodies.</li>
                <li>You must be in a quiet room (with no background noises).</li>
            </ul>
            If you cannot meet these requirements, please return the study.
            <hr>
            """
        ),
        time_estimate=3
    )

def instructions():
    return InfoPage(
        Markup(
            """
            <h3>Instructions</h3>
            <hr>
            You will hear short musical melodies. The melodies can eitehr be played by instruments or sung by other participants. 
            <br><br>
            Your task is to listen to the melodies and carefully evaluate them on liking and emotionality.
            <br><br>
            Please do not rate the melodies based on the quality of the voice or the recording, but only based on the quality of the music.
            <hr>
            """
        ),
        time_estimate=3
    )

