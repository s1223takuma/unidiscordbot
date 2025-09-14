import random
async def randomnum(ctx,min:int,max:int):
    if min >= max:
        await ctx.send("最小値は最大値より小さくしてください。")
        return
    randomnum = random.randint(min,max)
    await ctx.send(f"{randomnum}が出ました")