from markupsafe import Markup
from psynet.page import InfoPage


def welcome():
    return InfoPage(
        Markup(
            """
            <h3>Welcome</h3>
            <hr>
            Thanks for participating in this study! We aim to study how emotions are perceived in music.<br><br>
            In the study, you will hear melodies sung by other people and asked to rate them using different rating scales.
            <hr>
            """
        ),
        time_estimate=3
    )

def welcome_soniclogos():
    return InfoPage(
        Markup(
            """
            <h3>Welcome</h3>
            <hr>
            Thanks for participating in this study! We aim to study the perception of musical melodies.<br><br>
            In the study, you will hear melodies and asked to rate them using different rating scales.
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
            You will hear short musical melodies. The melodies can either be played by instruments or sung by other participants. 
            <br><br>
            Your task is to listen to the melodies and carefully evaluate them on liking and emotionality.
            <br><br>
            Please do not rate the melodies based on the quality of the voice or the recording, but only based on the quality of the music.
            <hr>
            """
        ),
        time_estimate=3
    )

def instructions_soniclogos():
    return InfoPage(
        Markup(
            """
            <h3>Instructions</h3>
            <hr>
            You will listen to short musical melodies and asked to evaluate them on different dimensions.
            <br><br>
            Please try to evaluate them as accurately as possible.
            <hr>
            """
        ),
        time_estimate=3
    )

