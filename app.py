# app.py
import streamlit as st
from datetime import date, datetime, timedelta
import uuid

# --- Page config ---
st.set_page_config(page_title="LifeQuest", page_icon="🎮", layout="wide")

# --- Simple CSS to make it look nicer ---
st.markdown(
    """
    <style>
    .big-title {font-size:32px; font-weight:700; text-align:center;}
    .sub {color: #6c757d; text-align:center; margin-bottom:18px;}
    .task-card {padding:10px 12px; border-radius:10px; background: #f7f9fc; margin-bottom:8px;}
    .small {font-size:12px; color:#666;}
    .btn {border-radius:8px;}
    .right-panel {background: linear-gradient(90deg, #ffffff, #f7fbff); padding:12px; border-radius:10px;}
    .badge-card {padding:8px; border-radius:8px; margin-bottom:6px; font-weight:600;}
    .badge-gold {background: #fff4d2; color: #b37d00;}
    .badge-silver {background: #f0f7ff; color: #1f6feb;}
    .badge-bronze {background: #fff2ec; color: #9a4b00;}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Initialize app state ---
if "user" not in st.session_state:
    st.session_state.user = {
        "name": "Sairam",
        "xp": 0,
        "coins": 0,
        "last_complete_date": None,
        "streak": 0,
        "badges": [],  # store unlocked badge ids/text
    }
if "tasks" not in st.session_state:
    st.session_state.tasks = []  # each task: {id, title, xp, created, completed_dates}

# --- Helper functions ---
def add_task(title, xp):
    st.session_state.tasks.append(
        {
            "id": str(uuid.uuid4()),
            "title": title,
            "xp": int(xp),
            "created": datetime.now().isoformat(),
            "completed_dates": [],
        }
    )

def check_badges():
    """
    Evaluate badge conditions and add any newly-unlocked badges to user['badges'].
    Show a message + small celebration for newly unlocked badges.
    """
    user = st.session_state.user
    newly_unlocked = []

    # define badge id -> (condition, label, style)
    badges_def = {
        "streak-3": (user["streak"] >= 3, "🔥 3-Day Streak (Bronze)", "badge-bronze"),
        "streak-7": (user["streak"] >= 7, "🥇 7-Day Streak (Gold)", "badge-gold"),
        "xp-100": (user["xp"] >= 100, "💡 100+ XP Achiever", "badge-silver"),
        "xp-300": (user["xp"] >= 300, "🚀 300+ XP Hero", "badge-gold"),
        "coins-50": (user["coins"] >= 50, "💰 50 Coins Collector", "badge-silver"),
        "coins-100": (user["coins"] >= 100, "👑 100 Coins Wealth Master", "badge-gold"),
    }

    for bid, (condition, label, style) in badges_def.items():
        if condition and bid not in user["badges"]:
            user["badges"].append(bid)
            newly_unlocked.append((bid, label, style))

    # Announce newly unlocked badges
    if newly_unlocked:
        # show all new badges to user
        for _, label, style in newly_unlocked:
            # style mapping for visible card
            if style == "badge-gold":
                st.markdown(f"<div class='badge-card badge-gold'>🎉 {label}</div>", unsafe_allow_html=True)
            elif style == "badge-silver":
                st.markdown(f"<div class='badge-card badge-silver'>🎉 {label}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='badge-card badge-bronze'>🎉 {label}</div>", unsafe_allow_html=True)
        # celebration once if there are new badges
        try:
            st.balloons()
        except Exception:
            pass  # some environments may not support balloons

def complete_task(task_id):
    today = date.today().isoformat()
    for t in st.session_state.tasks:
        if t["id"] == task_id:
            if today not in t["completed_dates"]:
                t["completed_dates"].append(today)
                st.session_state.user["xp"] += t["xp"]
                st.session_state.user["coins"] += max(1, t["xp"] // 10)
                update_streak()
                st.success(f"✅ +{t['xp']} XP — good job!")
                # Check if any badges unlocked by this completion
                check_badges()
            else:
                st.info("You've already completed this task today.")
            break

def delete_task(task_id):
    st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task_id]
    st.info("Task removed.")

def update_streak():
    today = date.today()
    last = st.session_state.user["last_complete_date"]
    if last:
        try:
            last_date = datetime.fromisoformat(last).date()
        except Exception:
            last_date = None
        if last_date == today - timedelta(days=1):
            st.session_state.user["streak"] += 1
        elif last_date == today:
            pass
        else:
            st.session_state.user["streak"] = 1
    else:
        st.session_state.user["streak"] = 1
    st.session_state.user["last_complete_date"] = datetime.now().isoformat()

def level_from_xp(xp):
    level = 1
    rem = xp
    while rem >= 100 * level:
        rem -= 100 * level
        level += 1
    next_level_xp = 100 * level
    return level, rem, next_level_xp

# --- Header ---
st.markdown('<div class="big-title">🎮 LifeQuest</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">Turn daily tasks into game quests — add tasks, complete them, earn XP & badges.</div>', unsafe_allow_html=True)

# --- Layout: tasks (left) and profile (right) ---
left, right = st.columns([2.4, 1])

with left:
    st.subheader("📋 Tasks")
    with st.expander("➕ Add a task (click to open)", expanded=True):
        new_title = st.text_input("Task title", placeholder="e.g. Study Python for 30 mins", key="new_title")

        # 🌟 Auto XP based on task type (smart XP logic)
        if new_title.strip() != "":
            ttext = new_title.lower()
            if "study" in ttext or "learn" in ttext or "python" in ttext or "dsa" in ttext:
                auto_xp = 50
            elif "exercise" in ttext or "workout" in ttext or "yoga" in ttext:
                auto_xp = 40
            elif "read" in ttext or "project" in ttext or "assignment" in ttext:
                auto_xp = 30
            elif "clean" in ttext or "organize" in ttext or "chores" in ttext:
                auto_xp = 20
            elif "movie" in ttext or "game" in ttext or "relax" in ttext:
                auto_xp = 10
            else:
                auto_xp = 15  # default XP
            st.info(f"💡 Suggested XP based on task type: {auto_xp} XP")
        else:
            auto_xp = 10

        add_col, clear_col = st.columns([1, 1])
        with add_col:
            if st.button("Add Task", key="add_task", help="Add this task to your list"):
                if new_title.strip() == "":
                    st.warning("Please enter a task title.")
                else:
                    add_task(new_title.strip(), auto_xp)
                    st.success(f"Task added with {auto_xp} XP!")
                    st.rerun()
        with clear_col:
            if st.button("Clear title", key="clear_title"):
                st.session_state.new_title = ""
                st.experimental_rerun()

    if not st.session_state.tasks:
        st.info("No tasks yet — add a task to get going!")
    else:
        for t in st.session_state.tasks:
            st.markdown('<div class="task-card">', unsafe_allow_html=True)
            tcols = st.columns([6, 1, 1])
            with tcols[0]:
                st.markdown(f"{t['title']}")
                st.markdown(f"<div class='small'>XP: {t['xp']} • Created: {t['created'][:10]}</div>", unsafe_allow_html=True)
            with tcols[1]:
                if st.button("✅ Complete", key=f"complete_{t['id']}", help="Mark task done for today"):
                    complete_task(t["id"])
                    st.rerun()
            with tcols[2]:
                if st.button("🗑", key=f"del_{t['id']}", help="Delete task"):
                    delete_task(t["id"])
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="right-panel">', unsafe_allow_html=True)
    st.subheader("🏆 Profile")
    user = st.session_state.user
    level, rem_xp, next_xp = level_from_xp(user["xp"])
    st.markdown(f"*Name:* {user['name']}")
    st.markdown(f"*Level:* {level}")
    st.metric("XP", f"{user['xp']} (need {next_xp-rem_xp} to next level)")
    # protect divide by zero
    try:
        st.progress(rem_xp / next_xp if next_xp else 0)
    except Exception:
        st.progress(0)
    st.markdown(f"*Coins:* {user['coins']}")
    st.markdown(f"🔥 Streak:** {user['streak']} days")
    st.divider()

    # --- Badges area (show unlocked badges and encourage user) ---
    st.subheader("🏅 Badges")
    # ensure badges exist as ids
    if "badges" not in user:
        user["badges"] = []
    # Map badge ids to display label & style for profile pane
    badge_map = {
        "streak-3": ("🔥 3-Day Streak (Bronze)", "badge-bronze"),
        "streak-7": ("🥇 7-Day Streak (Gold)", "badge-gold"),
        "xp-100": ("💡 100+ XP Achiever", "badge-silver"),
        "xp-300": ("🚀 300+ XP Hero", "badge-gold"),
        "coins-50": ("💰 50 Coins Collector", "badge-silver"),
        "coins-100": ("👑 100 Coins Wealth Master", "badge-gold"),
    }

    if user["badges"]:
        for bid in user["badges"]:
            label, style = badge_map.get(bid, (bid, "badge-silver"))
            if style == "badge-gold":
                st.markdown(f"<div class='badge-card badge-gold'>{label}</div>", unsafe_allow_html=True)
            elif style == "badge-silver":
                st.markdown(f"<div class='badge-card badge-silver'>{label}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='badge-card badge-bronze'>{label}</div>", unsafe_allow_html=True)
    else:
        st.info("No badges yet — keep completing tasks to earn rewards!")

    st.write("")  # spacing
    st.subheader("Quick Actions")
    q1, q2 = st.columns([1, 1])
    with q1:
        if st.button("Reset Progress", key="reset"):
            st.session_state.user = {
                "name": user["name"],
                "xp": 0,
                "coins": 0,
                "last_complete_date": None,
                "streak": 0,
                "badges": [],
            }
            st.success("Progress reset.")
            st.rerun()

    with q2:
        if st.button("Pre-fill sample tasks", key="prefill"):
            if not st.session_state.tasks:
                add_task("Study Python — 30m", 50)
                add_task("Exercise — 20m", 40)
                add_task("Read a chapter", 30)
                st.success("Sample tasks added.")
                # Check badges after prefill (in case sample data should unlock)
                check_badges()
            else:
                st.info("Tasks already present.")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.markdown("### 🥇 Leaderboard (demo)")
sample = [
    {"name": "Sairam", "xp": st.session_state.user["xp"]},
    {"name": "Ravi", "xp": max(0, st.session_state.user["xp"] - 24)},
    {"name": "Ananya", "xp": st.session_state.user["xp"] + 18},
]
sample_sorted = sorted(sample, key=lambda x: x["xp"], reverse=True)
for i, s in enumerate(sample_sorted, start=1):
    st.write(f"{i}. {s['name']} — {s['xp']} XP")

st.caption("Built quick for hackathon — add tasks, complete them, and show your progress!")