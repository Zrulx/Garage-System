import nextcord
from nextcord.ext import commands
from utils.vehicleUtils import *

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command("admin")
    async def admin(self, ctx: nextcord.Interaction):
        pass

    @admin.subcommand("vehicle")
    async def vehicle(self, ctx: nextcord.Interaction):
        pass

    @vehicle.subcommand("update_spawncode", "Update a spawn code for a vehicle slot")
    async def update_spawncode(self, ctx: nextcord.Interaction, slot: str = nextcord.SlashOption(description="Select the slot you are modifying the spawncode for", autocomplete=True), spawncode: str = nextcord.SlashOption(description="New Spawncode"), reason: str = nextcord.SlashOption(description="Reason you are changing the spawncode.")):
        try:
            split_string = slot.split("| ")
            
            if len(split_string) < 4:
                await ctx.send("No matching vehicle found for the selected slot. If this is an error, please open a ticket.", ephemeral=True)
                return
            
            owner_id = split_string[2]  # Assuming the owner_id is at position 2
            owner = await ctx.guild.fetch_member(owner_id)

            if owner:
                vehicles = getAllUserVehicles(owner)

                selected_vehicle = None
                
                for vehicle in vehicles:
                    vehicle_str = f"{vehicle[2]} | {vehicle[0]} | {vehicle[1]} | {vehicle[4]}" if vehicle[0] is not None else f"{vehicle[2]} | No Spawncode | {vehicle[1]} | {vehicle[4]}"
                    
                    if slot == vehicle_str:
                        selected_vehicle = vehicle
                        break
                
                if selected_vehicle is None:
                    await ctx.send("No matching vehicle found for the selected slot. If this is an error, please open a ticket.", ephemeral=True)
                    return

                updateVehicleSpawnCode(selected_vehicle, spawncode)
                await ctx.send(f"Updated {selected_vehicle[2]} slot's spawncode to {spawncode}", ephemeral=True)
            else:
                await ctx.send("Owner not found. Please ensure the owner ID is correct.", ephemeral=True)
        
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}", ephemeral=True)



    @update_spawncode.on_autocomplete("slot")
    async def update_spawncode_autocomplete(self, interaction: nextcord.Interaction, slot: str):
        vehicles = getAllVehicles()

        choices = [f"{vehicle[2]} | {vehicle[0]} | {vehicle[1]} | {vehicle[4]}" if vehicle[0] is not None else f"{vehicle[2]} | No Spawncode | {vehicle[1]} | {vehicle[4]}" for vehicle in vehicles]

        await interaction.response.send_autocomplete(choices)


    @vehicle.subcommand("removefriend", "Remove a friend from a vehicle slot")
    async def setfriend(self, ctx: nextcord.Interaction, slot: str = nextcord.SlashOption(description="Select the slot you are removing a friend from"), friend: nextcord.Member = nextcord.SlashOption(description="Select the friend you are removing")):
        pass

    

def setup(bot):
    bot.add_cog(AdminCommands(bot))
