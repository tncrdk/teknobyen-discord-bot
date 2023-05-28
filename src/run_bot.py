from __future__ import annotations
import discord
import event_handler
import os


def run_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    client = discord.Client(intents=intents)
    server = client.guilds[0]
    TOKEN = os.getenv("token")

    if TOKEN == None:
        raise KeyError("Fant ikke TOKEN i env-variablene")

    @client.event
    async def on_message(message: discord.Message) -> None:
        if message.author == client.user:
            return
        response = event_handler.handle_message(message)
        if response == None:
            return
        await event_handler.send_message(response)

    @client.event
    async def on_message_edit(
        message_before: discord.Message, message_after: discord.Message
    ) -> None:
        if message_before.author == client.user:
            return
        response = event_handler.handle_message_edit(message_before, message_after)
        if response == None:
            return
        await event_handler.send_message(response)

    @client.event
    async def on_message_delete(message: discord.Message) -> None:
        if message.author == client.user:
            return
        response = event_handler.handle_message_delete(message)
        if response == None:
            return
        await event_handler.send_message(response)

    @client.event
    async def on_member_join(member: discord.Member) -> None:
        response = event_handler.handle_member_join(member)
        if response == None:
            return
        await event_handler.send_message(response)

    client.run(TOKEN)


""" 
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
}

"""
