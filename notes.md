
Prosjekt
quotes-channel {
    legge til sitat
    slette sitat
    modifisere sitat
}
quotes-interactive {
    hente ut sitat basert på kriterier; command line
    (søke etter sitat)
    få link til sheet
}
general {
    generell info til nye medlemmer
    help
    legge til velkomst
    endre velkomst
    slette velkomst
}
geoguesser {
    sende ut meldinger til messenger om geoguesser
}
velkommen {
    velkommen, eller som denne personen ville sagt
}
commands {
    starter med !
}
CTF {
    Ved ny CTF -> lag ny kanal for den CTF-en og alle som trykker 
    delta blir lagt til i kanalen
}

--------------------------------------
handle_responses (finne ut hvilke funksjoner som skal kalles)
handle_message

lage en funksjon til hver kommando
hver kanal har en liste over hvilke kommandoer som er tilgjengelige

quotes {
    navn [til gruppe]
    sitat

    navn [til gruppe]
    sitat

    kunne slette ved hjelp av ID

    kunne hente ut alle sitatene i csv-format?


    {
        ID: {speaker, audience, quote}
    }

    For å endre på sitater på man eksplisitt bruke change-kommando;
    sikkerhet og vanskeligere for å fucke opp systemet
    Hvis noen endrer på en melding kommer det en feilmelding om at det ikke er støttet.
    Hvis det var meningen å endre på et sitat, må det gjøres manuelt med kommando.
}

Sletter ikke suksessfulle skrivinger. Kvitteringen inneholder alle formatterte sitat 
inklusiv ikke suksessfulle
Hva skjer ved feil i skriving til databasen. Går det an å endre på sitatet

Lage en backup-database med jevne mellomrom?

Sikkerhetshull å sjekke:
"" i strengen, hvordan håndterer python det?

se på ephemeral istedenfor å sende direkte til bruker

