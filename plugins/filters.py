import os
import pyrogram

from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

from database.filters_mdb import(
   add_filter,
   find_filter,
   get_filters,
   delete_fil,
   del_all,
   countfilters,
   allfilters
)

from database.connections_mdb import find_conn
from database.users_mdb import adduser, allusers

from plugins.helpers import parser,split_quotes



@Client.on_message(filters.command('add'))
async def addfilter(client, message):
      
    userid = message.from_user.id
    chat_type = message.chat.type
    args = message.text.split(None, 1)

    if chat_type == "private":
        grpid = await find_conn(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)
            return

    elif (chat_type == "group") or (chat_type == "supergroup"):
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if not ((st.status == "administrator") or (st.status == "creator") or (str(userid) in Config.AUTH_USERS)):
        return
        

    if len(args) < 2:
        await message.reply_text("Command Incomplete :(", quote=True)
        return
    
    extracted = split_quotes(args[1])
    text = extracted[0].lower()
   
    if not message.reply_to_message and len(extracted) < 2:
        await message.reply_text("Add some content to save your filter!", quote=True)
        return

    if len(extracted) >= 2:
        reply_text, btn = parser(extracted[1]) 
        fileid = None
        if not reply_text:
            await message.reply_text("You cannot have buttons alone, give some text to go with it!", quote=True)
            return

    elif message.reply_to_message and message.reply_to_message.reply_markup:
        try:
            rm = message.reply_to_message.reply_markup
            btn = rm.inline_keyboard
            msg = message.reply_to_message.document or\
                  message.reply_to_message.video or\
                  message.reply_to_message.photo or\
                  message.reply_to_message.audio or\
                  message.reply_to_message.animation or\
                  message.reply_to_message.sticker
            if msg:
                fileid = msg.file_id
                reply_text = message.reply_to_message.caption.html
            else:
                reply_text = message.reply_to_message.text.html
                fileid = None
        except:
            reply_text = ""
            btn = "[]" 
            fileid = None

    elif message.reply_to_message and message.reply_to_message.photo:
        try:
            fileid = message.reply_to_message.photo.file_id
            reply_text, btn = parser(message.reply_to_message.caption.html)
        except:
            reply_text = ""
            btn = "[]"

    elif message.reply_to_message and message.reply_to_message.video:
        try:
            fileid = message.reply_to_message.video.file_id
            reply_text,btn = parser(message.reply_to_message.caption.html)
        except:
            reply_text = ""
            btn = "[]"

    elif message.reply_to_message and message.reply_to_message.audio:
        try:
            fileid = message.reply_to_message.audio.file_id
            reply_text,btn = parser(message.reply_to_message.caption.html)
        except:
            reply_text = ""
            btn = "[]"  
   
    elif message.reply_to_message and message.reply_to_message.document:
        try:
            fileid = message.reply_to_message.document.file_id
            reply_text,btn = parser(message.reply_to_message.caption.html)
        except:
            reply_text = ""
            btn = "[]"

    elif message.reply_to_message and message.reply_to_message.animation:
        try:
            fileid = message.reply_to_message.animation.file_id
            reply_text,btn = parser(message.reply_to_message.caption.html)
        except:
            reply_text = ""
            btn = "[]"

    elif message.reply_to_message and message.reply_to_message.sticker:
        try:
            fileid = message.reply_to_message.sticker.file_id
            reply_text,btn =  parser(extracted[1])
        
        except:
            reply_text = ""
            btn = "[]"                   

    elif message.reply_to_message and message.reply_to_message.text:
        try:
            fileid = None
            reply_text, btn = parser(message.reply_to_message.text.html)
        except:
            reply_text = ""
            btn = "[]"

    else:
        return
    
    await add_filter(grp_id, text, reply_text, btn, fileid)

    await message.reply_text(
        f"Filter for  `{text}`  added in  **{title}**",
        quote=True,
        parse_mode="md"
    )


@Client.on_message(filters.command('viewfilters'))
async def get_all(client, message):
    userid = message.from_user.id
    chat_type = message.chat.type

    if chat_type == "private":
        grpid = await find_conn(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)
            return

    elif (chat_type == "group") or (chat_type == "supergroup"):
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if not ((st.status == "administrator") or (st.status == "creator") or (str(userid) in Config.AUTH_USERS)):
        return

    texts = await get_filters(grp_id)
    count = await countfilters(grp_id)
    if count:
        filterlist = f"Total number of filters in **{title}** : {count}\n\n"
        for text in texts:
            keywords = " ×  `{}`\n".format(text)
            if len(keywords) + len(filterlist) > 4096:
                await message.reply_text(
                    text=filterlist,
                    quote=True,
                    parse_mode="md"
                )
                filterlist = keywords
            else:
                filterlist += keywords
    else:
        filterlist = f"There are no active filters in **{title}**"

    await message.reply_text(
        text=filterlist,
        quote=True,
        parse_mode="md"
    )
        
@Client.on_message(filters.command('del'))
async def del_filter(client, message):
    userid = message.from_user.id
    chat_type = message.chat.type

    if chat_type == "private":
        grpid  = await find_conn(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)

    elif (chat_type == "group") or (chat_type == "supergroup"):
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if not ((st.status == "administrator") or (st.status == "creator") or (str(userid) in Config.AUTH_USERS)):
        return

    try:
        cmd, text = message.text.split(" ", 1)
    except:
        await message.reply_text(
            "<i>Mention the filtername which you wanna delete!</i>\n\n"
            "<code>/del filtername</code>\n\n"
            "Use /viewfilters to view all available filters",
            quote=True
        )
        return

    query = text.lower()

    await delete_fil(message, query, grp_id)
        

@Client.on_message(filters.command(["delall"]))
async def delallconfirm(client, message):
    userid = message.from_user.id
    chat_type = message.chat.type

    if chat_type == "private":
        grpid  = await find_conn(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)
            return

    elif (chat_type == "group") or (chat_type == "supergroup"):
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (st.status == "creator") or (str(userid) in Config.AUTH_USERS):
        await message.reply_text(
            f"This will delete all filters from '{title}'.\nDo you want to continue??",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text="YES",callback_data="delallconfirm")],
                [InlineKeyboardButton(text="CANCEL",callback_data="delallcancel")]
            ]),
            quote=True
        )


async def delall(client, message):
    userid = message.reply_to_message.from_user.id
    chat_type = message.chat.type

    if chat_type == "private":
        grpid  = await find_conn(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text(
                "I'm not connected to any groups!\nCheck /connections or connect to any groups",
                quote=True
            )
            return

    elif (chat_type == "group") or (chat_type == "supergroup"):
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (st.status == "creator") or (str(userid) in Config.AUTH_USERS):
        await del_all(message.reply_to_message, grp_id, title)


@Client.on_message((filters.private | filters.group) & filters.command(["status"]))
async def all_filters(client,message):
    if str(message.from_user.id) not in Config.AUTH_USERS:
        return

    chats, filters = await allfilters()
    users = await allusers()

    await message.reply_text(
        "**Current status of your bot!**\n\n"
        f"> __**{filters}** filters across **{chats}** chats__\n\n"
        f"> __**{users} users have interacted with your bot!**__",
        quote=True,
        parse_mode="md"
    )


@Client.on_message(filters.group & filters.all)
async def add_user(client,message):
    try:
        await adduser(
            str(message.from_user.id),
            str(message.from_user.username),
            str(message.from_user.first_name + message.from_user.last_name),
            str(message.from_user.dc_id)
        )
    except:
        pass


@Client.on_message(filters.group & filters.text)
async def recive_filter(client,message):
    group_id = message.chat.id
    name = message.text.lower()

    reply_text, btn, fileid = await find_filter(group_id, name) 

    if btn is None:
        return

    if fileid == "None":
        if btn == "[]":
            await message.reply_text(reply_text)
        else:
            button = eval(btn)
            await message.reply_text(
                reply_text,
                parse_mode="html",
                reply_markup=InlineKeyboardMarkup(button)
            )
    else:
        if btn == "[]":
            await message.reply_cached_media(
                fileid,
                caption=reply_text or ""
            )
        else:
            button = eval(btn) 
            await message.reply_cached_media(
                fileid,
                caption=reply_text or "",
                reply_markup=InlineKeyboardMarkup(button)
            )

      
