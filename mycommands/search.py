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