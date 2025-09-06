from ddgs import DDGS

async def search(ctx, *, query):
    with DDGS() as ddgs:
        results = list(ddgs.text(
            query,
            region="jp-jp",
            safesearch="off",
            timelimit=None,
            max_results=4
        ))
    if results:
        resultlink = "+".join(query.split(" "))
        reply = f"[{query}:google検索](https://google.com/search?q={resultlink})\n"
        reply += "\n".join([f"[{r['title']}]({r['href']})" for r in results])
        await ctx.send(f"🔎 **{query}** の検索結果:\n{reply}")
    else:
        await ctx.send(f"'{query}' に関する検索結果は見つかりませんでした。")

async def searchnews(ctx, *, query):
    with DDGS() as ddgs:
        results = list(ddgs.news(
            query,
            region="jp-jp",
            safesearch="off",
            timelimit=None,
            max_results=4
        ))
    if results:
        resultlink = "+".join(query.split(" "))
        reply = f"[{query}:googleニュース検索](https://google.com/search?q={resultlink}&tbm=nws)\n"
        reply += "\n".join([f"[{r['title']}]({r['url']})" for r in results])
        await ctx.send(f"📰 **{query}** のニュース検索結果:\n{reply}")
    else:
        await ctx.send(f"'{query}' に関するニュース検索結果は見つかりませんでした。")

async def searchimage(ctx, *, query):
    with DDGS() as ddgs:
        results = list(ddgs.images(
            query,
            region="jp-jp",
            safesearch="off",
            timelimit=None,
            max_results=4
        ))
    if results:
        resultlink = "+".join(query.split(" "))
        reply = f"[{query}:google画像検索](https://google.com/search?q={resultlink}&tbm=isch)\n"
        reply += "\n".join([f"[{r['title']}]({r['image']})" for r in results])
        await ctx.send(f"🖼️ **{query}** の画像検索結果:\n{reply}")
    else:
        await ctx.send(f"'{query}' に関する画像検索結果は見つかりませんでした。")