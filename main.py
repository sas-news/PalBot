from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
import os
import discord
from keep_alive import keep_alive
from discord import app_commands

address = os.environ['SERVER_ADDRESS']
password = os.environ['SERVER_PASSWORD']

# AzureのサブスクリプションID、リソースグループ、VMの名前を設定
subscription_id = os.environ['SUBSCRIPTION_ID']
resource_group_name = 'PalWorld_group'
vm_name = 'PalWorld'

# Azureサービスプリンシパルの認証情報を手動で指定
client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']
tenant_id = os.environ['TENANT_ID']
credentials = ClientSecretCredential(tenant_id, client_id, client_secret)
# ComputeManagementClientのインスタンスを作成
compute_client = ComputeManagementClient(credentials, subscription_id)
vm = compute_client.virtual_machines.get(resource_group_name, vm_name)

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
  print('ログインしました')
  # アクティビティを設定
  new_activity = f"PalWorld"
  await client.change_presence(activity=discord.Game(new_activity))
  # スラッシュコマンドを同期
  await tree.sync()


@tree.command(name="pal", description="PalServerを制御します")
@app_commands.describe(action="PalServerの操作を選択してください")
@app_commands.choices(action=[
    discord.app_commands.Choice(name="Start", value="start"),
    discord.app_commands.Choice(name="Stop", value="stop"),
    discord.app_commands.Choice(name="Status", value="status")
])
async def on_slash_command(interaction: discord.Interaction, action: str):
  if action == 'start':
    await interaction.response.defer()
    operation = compute_client.virtual_machines.begin_start(
        resource_group_name, vm_name)
    operation.wait()
    embed = discord.Embed(title=":white_check_mark: 起動しました",
                          description="PalServerが起動しました")
    embed.add_field(name="アドレス", value=address)
    embed.add_field(name="パスワード", value=password)
    await interaction.followup.send(embed=embed)
  if action == 'stop':
    operation = compute_client.virtual_machines.begin_deallocate(
        resource_group_name, vm_name)
    embed = discord.Embed(title=":octagonal_sign: 停止しました",
                          description="PalServerを停止します")
    embed.add_field(name="注意", value="少し待たないと起動できません")
    await interaction.response.send_message(embed=embed)
  if action == 'status':
    vm = compute_client.virtual_machines.get(resource_group_name, vm_name)
    if vm is not None:
      status = vm.instance_view.statuses
      embed = discord.Embed(title=":information_source: サーバーステータス",
                            description=status)
    else:
      embed = discord.Embed(title=":thinking: ステータスエラー",
                            description="ステータスを取得できませんでした")
    await interaction.response.send_message(embed=embed)


keep_alive()
TOKEN = os.getenv("DISCORD_TOKEN")
try:
  client.run(TOKEN)
except:
  os.system("kill 1")

# print(f"Starting VM {vm_name}...")

# print("VM started successfully.")
