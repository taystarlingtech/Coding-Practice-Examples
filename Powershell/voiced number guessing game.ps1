
#Guess a number. Be warned it speaks out lout in a synthesizer voice. 
Add-Type -AssemblyName System.Speech

[int]$guess = 0
[int]$attempt = 0
[int]$number = Get-Random -Minimum 1 -Maximum 100

$voice = New-Object System.Speech.Synthesis.SpeechSynthesizer
$voice.SelectVoice("Microsoft Zira Desktop")
$voice.Speak("Ahoy matey! I'm the GlaDos's less evil sister, and I have a secret!
              It's a number between 1 and 100. I'll give you 7 tries to guess it.")

do {
    $voice.SpeakAsync("What's your guess?") | Out-Null

    try {
        $guess = Read-Host "What's your guess?"

        if ($guess -lt 1 -or $guess -gt 100) {
            throw
        }
    }
    catch {
        $voice.Speak("Invalid number")
        continue
    }

    if ($guess -lt $number) {
        $voice.Speak("Too low!")
    }
    elseif ($guess -gt $number) {
        $voice.Speak("Too high!")
    }

    $attempt += 1
}
until ($guess -eq $number -or $attempt -eq 7)

if ($guess -eq $number) {
    $voice.Speak("Congratulations! You guessed Correctly")
}
else {
    $voice.Speak("Your out of guesses! Better luck next time, test subject!
                  My secret number was $number")
}