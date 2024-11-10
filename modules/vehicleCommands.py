import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View
from utils.vehicleUtils import *
from utils.tebexUtils import *
import configparser

config = configparser.ConfigParser()
config.read('config.ini')


class ConfirmView(View):
    def __init__(self, user, slot_type):
        super().__init__(timeout=None)
        self.user = user
        self.slot_type = slot_type

        # Confirm Button
        self.confirm_button = Button(label="Confirm", style=nextcord.ButtonStyle.green)
        self.confirm_button.callback = self.confirm
        self.add_item(self.confirm_button)

        # Deny Button
        self.deny_button = Button(label="Deny", style=nextcord.ButtonStyle.red)
        self.deny_button.callback = self.deny
        self.add_item(self.deny_button)

    async def confirm(self, interaction: nextcord.Interaction):
        # Disable buttons after confirmation
        self.confirm_button.disabled = True
        self.deny_button.disabled = True
        self.confirm_button.label = f"Confirmed by: {interaction.user}"
        await interaction.response.edit_message(view=self)

        # Register the vehicle when confirmed
        registerVehicle(self.user.id, self.slot_type, "other")

        # Send a direct message (ephemeral) to the original user
        await self.user.send(f"Your {self.slot_type} slot registration has been successfully confirmed!")

    async def deny(self, interaction: nextcord.Interaction):
        # Disable buttons after denial
        self.confirm_button.disabled = True
        self.deny_button.disabled = True
        self.deny_button.label = f"Denied by: {interaction.user}"
        await interaction.response.edit_message(view=self)

        # Send a direct message (ephemeral) to the original user
        await self.user.send(f"Your {self.slot_type} slot registration has been denied.")

class VehicleCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def alert(self, type, message, view=False):
        channel = await self.bot.fetch_channel(config.getint('logchannel', type))
        vview = view=view if view else None
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
            registerVehicle(ctx.user.id, slot_type, payment_proof)
            # instead of ctx.send it would be the user that originally ran this commanddd
            await ctx.send(f"You have succesfully registered a {slot_type} slot", ephemeral=True)
            return

        message = config.get('lang', "other_proof")
        message = message.format(user=ctx.user, slot_type=slot_type, screenshot_payment_proof=screenshot_payment_proof).replace(r'\n', '\n')
        confirm_view = ConfirmView(user=ctx.user, slot_type=slot_type)
        await self.alert("sale", message, view=confirm_view)

    @vehicle.subcommand("slot")
    async def slot(self, ctx: nextcord.Interaction):
        pass

    @slot.subcommand("list", "List all vehicles I own")
    async def slot_list(self, ctx: nextcord.Interaction, user: nextcord.Member = nextcord.SlashOption(description="Select the user you want to view slots for", required=False)):
        if not user:
            user = ctx.user
        vehicles = getAllUserVehicles(user)  # Retrieve the list of vehicles for the user
        

        embed = nextcord.Embed(title=f"Vehicles owned by {user.name}", description="Here are all the vehicles you own.", color=nextcord.Color.blue())
        
        if vehicles:
            for vehicle in vehicles:
                spawncode, owner_id, type, file_link, payment, status = vehicle
                
                embed.add_field(
                    name=f"Vehicle {type} | {spawncode or 'No Spawncode'}",
                    value=f"**Status:** {status or 'Unknown'}",
                    inline=False
                )
        else:
            embed.add_field(
                name="No vehicles found",
                value="You do not own any vehicles.",
                inline=False
            )

        await ctx.send(embed=embed, ephemeral=True)

    @slot.subcommand("view", "View a specific vehicle slot")
    async def slot_view(self, ctx: nextcord.Interaction, slot: str = nextcord.SlashOption(description="Select the slot you want to view", autocomplete=True)):
        vehicles = getAllUserVehicles(ctx.user)
        
        selected_vehicle = None
        for vehicle in vehicles:
            vehicle_str = f"{vehicle[2]} | {vehicle[0]}" if vehicle[0] is not None else f"{vehicle[2]} | No Spawncode"
            if slot == vehicle_str:
                selected_vehicle = vehicle
                break
        
        if selected_vehicle:
            print(selected_vehicle)
            spawncode, owner_id, type, file_link, payment, status, trust, ace, friend_slots, locked = selected_vehicle
            embed = nextcord.Embed(
                title=f"Vehicle Details - {type}",
                description=f"Details for the selected {type} vehicle.",
                color=nextcord.Color.green()
            )
            embed.add_field(name="Owner ID", value=str(owner_id), inline=False)
            embed.add_field(name="Spawncode", value=spawncode if spawncode else "No Spawncode", inline=False)
            embed.add_field(name="File Link", value=file_link if file_link else "No File Link", inline=False)
            embed.add_field(name="Status", value=status if status else "Unknown", inline=False)
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("No vehicle found for that slot.")

    @slot_view.on_autocomplete("slot")
    async def slot_view_autocomplete(self, interaction: nextcord.Interaction, slot: str):
        vehicles = getAllUserVehicles(interaction.user)

        choices = [f"{vehicle[2]} | {vehicle[0]}" if vehicle[0] is not None else f"{vehicle[2]} | No Spawncode" for vehicle in vehicles]

        await interaction.response.send_autocomplete(choices)


    @vehicle.subcommand("trust")
    async def trust(self, ctx: nextcord.Interaction):
        pass

    @trust.subcommand("purchasefriendslot", "Purchase an additional friend slot for a vehicle slot ($10.00 USD)")
    async def purchasefriendslot(self, ctx: nextcord.Interaction, slot: str = nextcord.SlashOption(description="Slot you are purchasing a friend slot for")):
        pass

    @trust.subcommand("setfriend", "Add a friend to a vehicle slot")
    async def setfriend(self, ctx: nextcord.Interaction, slot: str = nextcord.SlashOption(description="Select the slot you are adding a friend to"), friend: nextcord.Member = nextcord.SlashOption(description="Select the friend you are adding")):
        vehicles = getAllUserVehicles(ctx.user)
        
        selected_vehicle = None
        for vehicle in vehicles:
            vehicle_str = f"{vehicle[2]} | {vehicle[0]}" if vehicle[0] is not None else f"{vehicle[2]} | No Spawncode"
            if slot == vehicle_str:
                selected_vehicle = vehicle
                break

        if selected_vehicle:
            spawncode, owner_id, type, file_link, payment, status, trust, ace, friend_slots, locked = selected_vehicle
            addFriend(selected_vehicle, friend.id)
            await ctx.send(f"Succesfully added {friend.mention} as a friend to your {type} vehicle {spawncode}")


    @setfriend.on_autocomplete("slot")
    async def setfriend_autocomplete(self, interaction: nextcord.Interaction, slot: str):
        vehicles = getAllUserVehicles(interaction.user)

        choices = [f"{vehicle[2]} | {vehicle[0]}" if vehicle[0] is not None else f"{vehicle[2]} | No Spawncode" for vehicle in vehicles]

        await interaction.response.send_autocomplete(choices)
def setup(bot):
    bot.add_cog(VehicleCommands(bot))