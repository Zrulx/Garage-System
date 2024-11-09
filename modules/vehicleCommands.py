import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View
from utils.vehicleUtils import *
from utils.tebexUtils import *
import configparser

config = configparser.ConfigParser()
config.read('config.ini')


class ConfirmView(View):
    def __init__(self):
        super().__init__(timeout=None)

        # Confirm Button
        self.confirm_button = Button(label="Confirm", style=nextcord.ButtonStyle.green)
        self.confirm_button.callback = self.confirm
        self.add_item(self.confirm_button)

        # Deny Button
        self.deny_button = Button(label="Deny", style=nextcord.ButtonStyle.red)
        self.deny_button.callback = self.deny
        self.add_item(self.deny_button)

    async def confirm(self, interaction: nextcord.Interaction):
        self.confirm_button.disabled = True
        self.deny_button.disabled = True
        self.confirm_button.label = f"Confirmed by: {interaction.user}"
        await interaction.response.edit_message(view=self)
        await interaction.send("You confirmed!", ephemeral=True)

    async def deny(self, interaction: nextcord.Interaction):
        self.confirm_button.disabled = True
        self.deny_button.disabled = True
        self.confirm_button.label = f"Denied by: {interaction.user}"
        await interaction.response.edit_message(view=self)
        await interaction.send("You denied!", ephemeral=True)

class VehicleCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def alert(self, type, message, view=False):
        channel = await self.bot.fetch_channel(config.getint('logchannel', type))
        vview = ConfirmView() if view else None
        await channel.send(message, view=vview)

    @nextcord.slash_command("vehicle")
    async def vehicle(self, ctx: nextcord.Interaction):
        pass

    @vehicle.subcommand("help", "Get Help with the Vehicle Slot System")
    async def help(self, ctx: nextcord.Interaction):
        await ctx.send("Not yet complete please message one of the devs.", ephemeral=True)

    @vehicle.subcommand("registerslot", "Register a paid slot for a vehicle")
    async def registerslot(self, ctx: nextcord.Interaction, slot_type: str = nextcord.SlashOption(description="Select the type of slot you are registering", choices=["CIV", "LEO", "Speciality"]), payment_proof: str = nextcord.SlashOption(description="Tebex ID if Slot or Write Other if not Tebex Package Purchase"), screenshot_payment_proof: nextcord.Attachment = nextcord.SlashOption(description="Screenshot of your payment proof"), vehicle_file_link: str = nextcord.SlashOption(description="Link to the vehicle file") ):
        if payment_proof.lower() != "other":
            payment = confirmTebexID(payment_proof)
            # if not a valid tebex id
            if not payment:
                await ctx.send("Invalid Tebex ID", ephemeral=True)
                return
            # if a valid tebex id
            message = config.get('lang', "valid_tebex_id")
            message = message.format(user=ctx.user, slot_type=slot_type, payment_proof=payment_proof, screenshot_payment_proof=screenshot_payment_proof).replace(r'\n', '\n')
            await self.alert("alert", message)
            # register the vehicle here:
            registerVehicle(ctx.user.id, slot_type)
            await ctx.send(f"You have succesfully registered a {slot_type} slot", ephemeral=True)
            return

        message = config.get('lang', "other_proof")
        message = message.format(user=ctx.user, slot_type=slot_type, screenshot_payment_proof=screenshot_payment_proof).replace(r'\n', '\n')
        await self.alert("sale", message, view=True)

    @vehicle.subcommand("slot")
    async def slot(self, ctx: nextcord.Interaction):
        pass

    @slot.subcommand("list", "List all vehicles I own")
    async def slot_list(self, ctx: nextcord.Interaction, user: nextcord.Member = nextcord.SlashOption(description="Select the user you want to view slots for", required=False)):
        pass
    
    @slot.subcommand("view", "View a specific vehicle slot")
    async def slot_list(self, ctx: nextcord.Interaction, slot: str = nextcord.SlashOption(description="Select the slot you want to view", autocomplete=True)):
        await ctx.send("debug")

    @slot_list.on_autocomplete("slot")
    async def slot_list_autocomplete(self, interaction: nextcord.Interaction, slot: str):
        vehicles = getAllUserVehicles(interaction)
        print(vehicles)
        choices = [f"{vehicle[2]} | {vehicle[0]}" if vehicle[0] is not None else f"{vehicle[2]} | No Spawncode" for vehicle in vehicles]
        await interaction.response.send_autocomplete(choices)

    
def setup(bot):
    bot.add_cog(VehicleCommands(bot))