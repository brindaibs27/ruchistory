
import streamlit as st
import json
import os
from google import genai

# ============================================================
# PAGE SETUP
# ============================================================

st.set_page_config(
    page_title="Ruchi Story | Make More of What You Have",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# STYLING
# ============================================================

st.markdown("""
<style>
.block-container {
    max-width: 1180px;
    padding-top: 1.5rem;
    padding-bottom: 4rem;
}

[data-testid="stMetric"] {
    border: 1px solid rgba(49, 82, 47, 0.15);
    border-radius: 14px;
    padding: 12px;
}

.ruchi-intro {
    text-align: center;
    max-width: 760px;
    margin: -5px auto 20px auto;
    font-size: 1.05rem;
    color: #53624f;
}

.small-note {
    font-size: 0.85rem;
    color: #777;
}

.platform-flow {
    padding: 14px 18px;
    border: 1px solid rgba(49, 82, 47, 0.16);
    border-radius: 14px;
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {
    # Original Ruchi journey
    "saved_recipes": [],
    "saved_links": [],
    "meal_options": [],
    "current_recipe": None,
    "cooking_step": 0,
    "cooking_started": False,
    "cooking_history": [],
    "last_inputs": {},

    # Ruchi Story platform
    "selected_provider": None,
    "followed_creators": [],
    "saved_creators": [],
    "consultation_requests": [],
    "community_posts": [],
    "liked_posts": [],
    "saved_posts": [],
    "reported_posts": []
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# GEMINI
# ============================================================

def get_client():
    try:
        return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    except Exception:
        return None


def clean_json_response(raw):
    raw = raw.strip()

    if raw.startswith("```json"):
        raw = raw[7:]

    if raw.startswith("```"):
        raw = raw[3:]

    if raw.endswith("```"):
        raw = raw[:-3]

    return raw.strip()


def generate_meal_options(
    craving,
    ingredients,
    servings,
    diet,
    allergies,
    spice
):
    client = get_client()

    if client is None:
        return None, (
            "Gemini API key is unavailable. "
            "Add GEMINI_API_KEY to Streamlit Secrets."
        )

    prompt = f"""
You are Ruchi, an intelligent everyday kitchen assistant.

Ruchi helps people make better use of food and ingredients
they already have.

USER CONTEXT

Craving:
{craving}

Ingredients already available:
{ingredients}

Servings:
{servings}

Dietary preference:
{diet}

Allergies / ingredients to avoid:
{allergies}

Spice preference:
{spice}

Suggest exactly THREE practical meals.

Priorities:
1. Use the ingredients already available.
2. Match the craving where reasonable.
3. Minimise unnecessary extra ingredients.
4. Respect dietary preferences and allergies.
5. Keep meals realistic for home cooking.
6. Give three meaningfully different options.

Return ONLY valid JSON in this exact structure:

{{
  "options": [
    {{
      "dish_name": "Dish name",
      "description": "Short appetising description",
      "why_it_fits": "Why this fits the user's kitchen"
    }},
    {{
      "dish_name": "Dish name",
      "description": "Short appetising description",
      "why_it_fits": "Why this fits the user's kitchen"
    }},
    {{
      "dish_name": "Dish name",
      "description": "Short appetising description",
      "why_it_fits": "Why this fits the user's kitchen"
    }}
  ]
}}
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        data = json.loads(
            clean_json_response(response.text)
        )

        return data["options"], None

    except Exception as e:
        return None, str(e)


def generate_recipe(
    dish,
    ingredients,
    servings,
    diet,
    allergies,
    spice
):
    client = get_client()

    if client is None:
        return None, (
            "Gemini API key is unavailable. "
            "Add GEMINI_API_KEY to Streamlit Secrets."
        )

    prompt = f"""
You are Ruchi, an intelligent everyday kitchen assistant.

Create a practical home-cooking recipe.

Dish:
{dish}

Ingredients the user already has:
{ingredients}

Servings:
{servings}

Dietary preference:
{diet}

Allergies / ingredients to avoid:
{allergies}

Spice preference:
{spice}

Return ONLY valid JSON:

{{
  "dish_name": "Dish name",
  "description": "One short appetising description",
  "cooking_time": "Example: 25 minutes",
  "servings": {servings},
  "ingredients": [
    {{
      "name": "Ingredient",
      "quantity": "Quantity",
      "already_have": true
    }}
  ],
  "steps": [
    "Step one",
    "Step two"
  ],
  "substitutions": [
    "Useful substitution"
  ],
  "nutrition": {{
    "calories": "Approximate calories per serving",
    "protein": "Approximate protein per serving"
  }}
}}

Mark already_have as true only when that ingredient is
reasonably present in the user's available ingredient list.

Nutrition must be clearly approximate.
Do not include any text outside the JSON.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        data = json.loads(
            clean_json_response(response.text)
        )

        return data, None

    except Exception as e:
        return None, str(e)


# ============================================================
# ILLUSTRATIVE PLATFORM PARTICIPANTS
# ============================================================

GROCERY_PROVIDERS = [
    {
        "name": "Fresh Basket",
        "rating": 4.7,
        "verified": True,
        "delivery": "25–35 min",
        "price": "₹₹",
        "categories": [
            "Vegetables", "Fruits", "Dairy",
            "Paneer", "Herbs", "Spices"
        ]
    },
    {
        "name": "Daily Pantry",
        "rating": 4.5,
        "verified": True,
        "delivery": "35–45 min",
        "price": "₹",
        "categories": [
            "Rice", "Flour", "Lentils",
            "Oil", "Spices", "Sauces"
        ]
    },
    {
        "name": "Green Cart",
        "rating": 4.8,
        "verified": True,
        "delivery": "40–50 min",
        "price": "₹₹",
        "categories": [
            "Vegetables", "Fruits", "Herbs",
            "Tofu", "Vegan", "Organic"
        ]
    },
    {
        "name": "Kitchen Stop",
        "rating": 4.3,
        "verified": False,
        "delivery": "30–40 min",
        "price": "₹",
        "categories": [
            "Dairy", "Bread", "Eggs",
            "Vegetables", "Spices", "Sauces"
        ]
    }
]


CREATORS = [
    {
        "name": "Aarohi Cooks",
        "speciality": "Quick Indian Home Cooking",
        "rating": 4.8,
        "followers": "18K",
        "verified": True,
        "description": "Simple Indian meals for busy days.",
        "tags": ["Quick", "Indian", "Vegetarian"]
    },
    {
        "name": "The Student Kitchen",
        "speciality": "Budget & Beginner Meals",
        "rating": 4.6,
        "followers": "11K",
        "verified": True,
        "description": "Low-effort meals using everyday ingredients.",
        "tags": ["Budget", "Beginner", "Quick"]
    },
    {
        "name": "Plant Plate",
        "speciality": "Plant-Based Cooking",
        "rating": 4.7,
        "followers": "14K",
        "verified": True,
        "description": "Vegetarian and vegan meal inspiration.",
        "tags": ["Vegetarian", "Vegan", "Healthy"]
    },
    {
        "name": "Spice Route Stories",
        "speciality": "Regional Indian Food",
        "rating": 4.9,
        "followers": "22K",
        "verified": True,
        "description": "Regional recipes, flavours and techniques.",
        "tags": ["Indian", "Regional", "Traditional"]
    }
]


NUTRITIONISTS = [
    {
        "name": "Meera Shah",
        "speciality": "Balanced Everyday Nutrition",
        "focus": ["General Wellness", "Balanced Diet"],
        "experience": "8 years",
        "rating": 4.8,
        "verified": True
    },
    {
        "name": "Ananya Rao",
        "speciality": "Sports & High-Protein Nutrition",
        "focus": ["High Protein", "Fitness"],
        "experience": "6 years",
        "rating": 4.7,
        "verified": True
    },
    {
        "name": "Nisha Patel",
        "speciality": "Plant-Based Nutrition",
        "focus": ["Vegetarian", "Vegan"],
        "experience": "5 years",
        "rating": 4.6,
        "verified": True
    },
    {
        "name": "Rhea Menon",
        "speciality": "Everyday Meal Planning",
        "focus": ["Meal Planning", "General Wellness"],
        "experience": "7 years",
        "rating": 4.5,
        "verified": True
    }
]


COMMUNITY_SEED_POSTS = [
    {
        "id": "sample_1",
        "user": "Maya",
        "meal": "Leftover Rice Tikkis",
        "text": (
            "Turned yesterday's rice into crispy tikkis "
            "with onion, chilli and spices."
        ),
        "likes": 18
    },
    {
        "id": "sample_2",
        "user": "Kabir",
        "meal": "Quick Paneer Bowl",
        "text": (
            "Used paneer, capsicum and leftover curd. "
            "Roasted cumin worked really well in the dressing."
        ),
        "likes": 24
    },
    {
        "id": "sample_3",
        "user": "Tara",
        "meal": "Vegetable Wrap",
        "text": (
            "Used the vegetables left in my fridge before "
            "grocery day and added a quick yoghurt dip."
        ),
        "likes": 13
    }
]


# ============================================================
# HELPERS
# ============================================================

def get_missing_ingredients():
    recipe = st.session_state.current_recipe

    if not recipe:
        return []

    return [
        item
        for item in recipe.get("ingredients", [])
        if not item.get("already_have", False)
    ]


def get_current_dish():
    recipe = st.session_state.current_recipe

    if not recipe:
        return None

    return recipe.get("dish_name", "Your Meal")


# ============================================================
# HEADER
# ============================================================

left, centre, right = st.columns([1, 2.2, 1])

with centre:
    if os.path.exists("ruchi_story_logo.png"):
        st.image(
            "ruchi_story_logo.png",
            use_container_width=True
        )
    else:
        st.title("Ruchi Story")
        st.caption("Make More of What You Have.")

st.markdown(
    """
    <div class="ruchi-intro">
    From personal kitchen intelligence to a connected food
    ecosystem — decide what to cook, complete your meal,
    discover people and share what you create.
    </div>
    """,
    unsafe_allow_html=True
)

st.caption(
    "Participant listings in Ruchi Story are illustrative and "
    "are used to demonstrate how interactions on the platform work."
)

st.markdown("---")


# ============================================================
# NAVIGATION
# ============================================================

(
    kitchen_tab,
    grocery_tab,
    creator_tab,
    nutrition_tab,
    community_tab,
    cooking_tab,
    insights_tab,
    library_tab,
    plus_tab,
    future_tab
) = st.tabs([
    "🍳 My Kitchen",
    "🛒 Grocery",
    "🎥 Creators",
    "🥗 Nutritionists",
    "🤝 Community",
    "👩‍🍳 Cooking Mode",
    "📊 Kitchen Insights",
    "📚 My Library",
    "✨ Ruchi Plus",
    "🌱 What's Next"
])


# ============================================================
# 1. MY KITCHEN
# ============================================================

with kitchen_tab:

    st.header("What can we make today?")

    st.write(
        "Tell Ruchi Story what you have and what you're in the "
        "mood for. We'll help you turn it into a meal."
    )

    craving = st.text_input(
        "What are you in the mood for?",
        placeholder=(
            "Something spicy, comforting, light, high-protein..."
        )
    )

    ingredients = st.text_area(
        "What's already in your kitchen?",
        placeholder=(
            "Paneer, tomatoes, onion, curd, capsicum..."
        )
    )

    st.subheader("Make it yours")

    c1, c2 = st.columns(2)

    with c1:
        servings = st.number_input(
            "Servings",
            min_value=1,
            max_value=10,
            value=2
        )

        diet = st.selectbox(
            "Dietary preference",
            [
                "No preference",
                "Vegetarian",
                "Vegan",
                "Eggetarian"
            ]
        )

    with c2:
        spice = st.selectbox(
            "Spice preference",
            [
                "Mild",
                "Medium",
                "Spicy",
                "Very spicy"
            ]
        )

        allergies = st.text_input(
            "Anything to avoid?",
            placeholder="Peanuts, mushrooms..."
        )

    if st.button(
        "✨ Show Me What I Can Make",
        type="primary",
        use_container_width=True
    ):

        if not craving.strip() and not ingredients.strip():
            st.warning(
                "Give Ruchi Story a craving or a few ingredients "
                "to start with."
            )

        else:
            st.session_state.last_inputs = {
                "craving": craving,
                "ingredients": ingredients,
                "servings": servings,
                "diet": diet,
                "allergies": allergies,
                "spice": spice
            }

            with st.spinner(
                "Looking through your kitchen..."
            ):
                options, error = generate_meal_options(
                    craving,
                    ingredients,
                    servings,
                    diet,
                    allergies,
                    spice
                )

            if error:
                st.error(
                    "Ruchi Story couldn't generate meal options. "
                    f"{error}"
                )

            else:
                st.session_state.meal_options = options
                st.session_state.current_recipe = None
                st.session_state.cooking_started = False
                st.session_state.cooking_step = 0


    # --------------------------------------------------------
    # THREE MEAL OPTIONS
    # --------------------------------------------------------

    if st.session_state.meal_options:

        st.markdown("---")
        st.subheader("🍽️ Here's what you could make")

        st.caption(
            "Three practical choices based on what you already have."
        )

        meal_cols = st.columns(3)

        for i, option in enumerate(
            st.session_state.meal_options[:3]
        ):
            with meal_cols[i]:

                st.markdown(
                    f"### {option.get('dish_name', 'Meal')}"
                )

                st.write(
                    option.get("description", "")
                )

                st.info(
                    option.get(
                        "why_it_fits",
                        "A practical option for your kitchen."
                    )
                )

                if st.button(
                    "Choose this meal",
                    key=f"choose_meal_{i}",
                    use_container_width=True
                ):
                    data = st.session_state.last_inputs

                    with st.spinner(
                        "Building your meal..."
                    ):
                        recipe, error = generate_recipe(
                            option.get("dish_name", ""),
                            data["ingredients"],
                            data["servings"],
                            data["diet"],
                            data["allergies"],
                            data["spice"]
                        )

                    if error:
                        st.error(
                            "Ruchi Story couldn't build the recipe. "
                            f"{error}"
                        )

                    else:
                        st.session_state.current_recipe = recipe
                        st.session_state.cooking_step = 0
                        st.session_state.cooking_started = False
                        st.rerun()


    # --------------------------------------------------------
    # INGREDIENT INTELLIGENCE
    # --------------------------------------------------------

    recipe = st.session_state.current_recipe

    if recipe:

        st.markdown("---")

        st.header(
            recipe.get("dish_name", "Your Meal")
        )

        st.write(
            recipe.get("description", "")
        )

        ingredient_list = recipe.get(
            "ingredients",
            []
        )

        already_have = [
            item for item in ingredient_list
            if item.get("already_have", False)
        ]

        missing = [
            item for item in ingredient_list
            if not item.get("already_have", False)
        ]

        m1, m2, m3 = st.columns(3)

        m1.metric(
            "⏱️ Cooking Time",
            recipe.get("cooking_time", "N/A")
        )

        m2.metric(
            "🍽️ Servings",
            recipe.get("servings", "-")
        )

        m3.metric(
            "🥕 Already Have",
            f"{len(already_have)}/{len(ingredient_list)}"
        )

        st.subheader("🥕 Ingredient Intelligence")

        have_col, need_col = st.columns(2)

        with have_col:
            st.markdown("#### Already in your kitchen")

            if already_have:
                for item in already_have:
                    st.write(
                        f"✓ **{item.get('name', 'Ingredient')}** "
                        f"— {item.get('quantity', '')}"
                    )
            else:
                st.write(
                    "No ingredients were matched."
                )

        with need_col:
            st.markdown("#### You may still need")

            if missing:
                for item in missing:
                    st.write(
                        f"○ **{item.get('name', 'Ingredient')}** "
                        f"— {item.get('quantity', '')}"
                    )

                st.info(
                    "These ingredients can now connect to the "
                    "Grocery side of Ruchi Story."
                )

            else:
                st.success(
                    "You already have everything you need."
                )

        st.markdown("---")

        st.subheader("🔄 Easy Swaps")

        substitutions = recipe.get(
            "substitutions",
            []
        )

        if substitutions:
            for substitution in substitutions:
                st.write(f"• {substitution}")
        else:
            st.write("No substitutions needed.")

        st.subheader("🥗 Nutrition Snapshot")

        nutrition = recipe.get(
            "nutrition",
            {}
        )

        n1, n2 = st.columns(2)

        n1.metric(
            "Approx. calories / serving",
            nutrition.get("calories", "N/A")
        )

        n2.metric(
            "Approx. protein / serving",
            nutrition.get("protein", "N/A")
        )

        st.caption(
            "Nutrition values are approximate and are not a "
            "substitute for professional medical or dietary advice."
        )

        st.markdown("---")

        st.subheader("🌐 Continue Your Story")

        p1, p2, p3, p4 = st.columns(4)

        with p1:
            st.markdown("**🛒 Complete the Meal**")
            st.write(
                "Compare grocery providers for ingredients "
                "you still need."
            )

        with p2:
            st.markdown("**🎥 Get Inspired**")
            st.write(
                "Discover food creators and save the ones "
                "you like."
            )

        with p3:
            st.markdown("**🥗 Get Guidance**")
            st.write(
                "Find nutrition professionals based on "
                "your food goals."
            )

        with p4:
            st.markdown("**🤝 Share**")
            st.write(
                "After cooking, share your experience with "
                "the community."
            )

        save_col, cook_col = st.columns(2)

        with save_col:
            if st.button(
                "♡ Save for Later",
                use_container_width=True
            ):
                if (
                    recipe not in
                    st.session_state.saved_recipes
                ):
                    st.session_state.saved_recipes.append(
                        recipe
                    )

                st.success("Saved to My Library.")

        with cook_col:
            if st.button(
                "👩‍🍳 Start Cooking",
                type="primary",
                use_container_width=True
            ):
                st.session_state.cooking_started = True
                st.session_state.cooking_step = 0

                st.success(
                    "Cooking Mode is ready. Open the "
                    "👩‍🍳 Cooking Mode tab."
                )


# ============================================================
# 2. GROCERY PROVIDERS
# ============================================================

with grocery_tab:

    st.header("🛒 Complete Your Meal")

    st.write(
        "Ruchi Story connects missing ingredients from your "
        "meal with relevant grocery providers."
    )

    missing_items = get_missing_ingredients()

    if missing_items:
        st.subheader("Your missing ingredients")

        for item in missing_items:
            st.write(
                f"• {item.get('name', 'Ingredient')} "
                f"— {item.get('quantity', '')}"
            )

    else:
        st.info(
            "Choose a meal in My Kitchen to automatically "
            "bring its missing ingredients here."
        )

        manual_items = st.text_input(
            "Or enter ingredients to explore",
            placeholder="Coriander, paneer, soy sauce"
        )

        if manual_items.strip():
            st.write(
                "**Looking for:** "
                + ", ".join(
                    x.strip()
                    for x in manual_items.split(",")
                    if x.strip()
                )
            )

    st.markdown("---")

    sort_by = st.selectbox(
        "Sort providers by",
        [
            "Recommended",
            "Highest rating",
            "Fastest fulfilment"
        ]
    )

    verified_only = st.checkbox(
        "Show verified providers only"
    )

    providers = GROCERY_PROVIDERS.copy()

    if verified_only:
        providers = [
            p for p in providers
            if p["verified"]
        ]

    if sort_by == "Highest rating":
        providers = sorted(
            providers,
            key=lambda p: p["rating"],
            reverse=True
        )

    elif sort_by == "Fastest fulfilment":
        providers = sorted(
            providers,
            key=lambda p: int(
                p["delivery"].split("–")[0]
            )
        )

    for i, provider in enumerate(providers):

        with st.container(border=True):

            verified = (
                " ✓ Verified"
                if provider["verified"]
                else ""
            )

            st.subheader(
                provider["name"] + verified
            )

            st.write(
                f"⭐ {provider['rating']}  ·  "
                f"🚚 {provider['delivery']}  ·  "
                f"{provider['price']}"
            )

            st.caption(
                "Categories: "
                + " • ".join(provider["categories"])
            )

            if st.button(
                "Select Provider",
                key=f"provider_{i}",
                use_container_width=True
            ):
                st.session_state.selected_provider = (
                    provider["name"]
                )

                st.success(
                    f"{provider['name']} selected."
                )

            if (
                st.session_state.selected_provider
                == provider["name"]
            ):
                st.info(
                    "In a live version, your ingredient request "
                    "would now move toward this provider."
                )

                st.caption(
                    "No order, payment or real provider request "
                    "has been created."
                )

    with st.expander(
        "How does value exchange happen here?"
    ):
        st.write(
            "The user gets a relevant route to complete the meal. "
            "The grocery provider gets relevant purchase intent. "
            "A future transaction-linked commission could allow "
            "Ruchi Story to monetise when successful value exchange "
            "occurs."
        )


# ============================================================
# 3. FOOD CREATORS
# ============================================================

with creator_tab:

    st.header("🎥 Discover Food Creators")

    st.write(
        "Move from a meal decision to inspiration, techniques "
        "and ideas from food creators."
    )

    current_dish = get_current_dish()

    if current_dish:
        st.success(
            f"Your current meal: **{current_dish}**"
        )

    creator_filter = st.selectbox(
        "What kind of inspiration do you want?",
        [
            "All",
            "Quick",
            "Indian",
            "Vegetarian",
            "Vegan",
            "Budget",
            "Beginner"
        ]
    )

    if creator_filter == "All":
        creators = CREATORS
    else:
        creators = [
            creator
            for creator in CREATORS
            if creator_filter in creator["tags"]
        ]

    for i, creator in enumerate(creators):

        with st.container(border=True):

            verified = (
                " ✓ Verified"
                if creator["verified"]
                else ""
            )

            st.subheader(
                creator["name"] + verified
            )

            st.write(
                f"**{creator['speciality']}**"
            )

            st.write(
                creator["description"]
            )

            st.write(
                f"⭐ {creator['rating']}  ·  "
                f"👥 {creator['followers']} followers"
            )

            if current_dish:
                st.caption(
                    "Recommended within your current food journey: "
                    f"{current_dish}"
                )

            c1, c2 = st.columns(2)

            with c1:
                if (
                    creator["name"]
                    in st.session_state.followed_creators
                ):
                    st.button(
                        "✓ Following",
                        key=f"following_{i}",
                        disabled=True,
                        use_container_width=True
                    )

                else:
                    if st.button(
                        "＋ Follow",
                        key=f"follow_{i}",
                        use_container_width=True
                    ):
                        st.session_state.followed_creators.append(
                            creator["name"]
                        )
                        st.rerun()

            with c2:
                if st.button(
                    "🔖 Save Creator",
                    key=f"save_creator_{i}",
                    use_container_width=True
                ):
                    if (
                        creator["name"]
                        not in st.session_state.saved_creators
                    ):
                        st.session_state.saved_creators.append(
                            creator["name"]
                        )

                    st.success("Creator saved.")


# ============================================================
# 4. NUTRITIONISTS
# ============================================================

with nutrition_tab:

    st.header("🥗 Find Nutrition Guidance")

    st.write(
        "Ruchi Story can connect users who want deeper food "
        "guidance with relevant nutrition professionals."
    )

    st.caption(
        "These illustrative profiles do not provide medical "
        "advice or real consultations."
    )

    goal = st.selectbox(
        "What are you looking for?",
        [
            "General Wellness",
            "Balanced Diet",
            "High Protein",
            "Fitness",
            "Vegetarian",
            "Vegan",
            "Meal Planning"
        ]
    )

    matches = [
        person
        for person in NUTRITIONISTS
        if goal in person["focus"]
    ]

    if not matches:
        matches = NUTRITIONISTS

    st.write(
        f"**Matches for:** {goal}"
    )

    for i, person in enumerate(matches):

        with st.container(border=True):

            verified = (
                " ✓ Verified"
                if person["verified"]
                else ""
            )

            st.subheader(
                person["name"] + verified
            )

            st.write(
                f"**{person['speciality']}**"
            )

            st.write(
                f"⭐ {person['rating']}  ·  "
                f"Experience: {person['experience']}"
            )

            st.caption(
                "Focus: "
                + " • ".join(person["focus"])
            )

            if st.button(
                "Request Consultation",
                key=f"consult_{i}",
                use_container_width=True
            ):
                request = {
                    "nutritionist": person["name"],
                    "goal": goal
                }

                if (
                    request not in
                    st.session_state.consultation_requests
                ):
                    st.session_state.consultation_requests.append(
                        request
                    )

                st.success(
                    "Consultation request recorded for this "
                    "platform demonstration."
                )

                st.caption(
                    "No real appointment or payment was created."
                )


# ============================================================
# 5. COMMUNITY
# ============================================================

with community_tab:

    st.header("🤝 Ruchi Community")

    st.write(
        "Turn individual cooking experiences into shared value."
    )

    share_tab, discover_tab = st.tabs([
        "Share My Story",
        "Discover"
    ])

    with share_tab:

        history = st.session_state.cooking_history

        if history:
            meal_choices = [
                meal.get("dish_name", "Meal")
                for meal in history
            ]

            shared_meal = st.selectbox(
                "What did you make?",
                meal_choices
            )

        elif st.session_state.current_recipe:
            shared_meal = (
                st.session_state.current_recipe.get(
                    "dish_name",
                    "My Meal"
                )
            )

            st.write(
                f"Meal: **{shared_meal}**"
            )

        else:
            shared_meal = st.text_input(
                "What did you make?",
                placeholder="Vegetable pulao"
            )

        display_name = st.text_input(
            "Display name",
            value="Ruchi Home Cook"
        )

        story = st.text_area(
            "Share your cooking story or tip",
            placeholder=(
                "What worked? Did you substitute anything? "
                "What would you do differently next time?"
            )
        )

        if st.button(
            "🤝 Share with Community",
            type="primary",
            use_container_width=True
        ):

            if (
                str(shared_meal).strip()
                and story.strip()
            ):
                post_id = (
                    "user_"
                    + str(
                        len(
                            st.session_state.community_posts
                        ) + 1
                    )
                )

                st.session_state.community_posts.append({
                    "id": post_id,
                    "user": (
                        display_name.strip()
                        or "Ruchi Home Cook"
                    ),
                    "meal": str(shared_meal),
                    "text": story.strip(),
                    "likes": 0
                })

                st.success(
                    "Your Story has been shared."
                )

            else:
                st.warning(
                    "Add a meal and a short story first."
                )

    with discover_tab:

        posts = (
            st.session_state.community_posts
            + COMMUNITY_SEED_POSTS
        )

        for post in reversed(posts):

            with st.container(border=True):

                st.caption(
                    f"Shared by {post['user']}"
                )

                st.subheader(
                    post["meal"]
                )

                st.write(
                    post["text"]
                )

                post_id = post["id"]

                like_count = (
                    post.get("likes", 0)
                    + (
                        1
                        if post_id
                        in st.session_state.liked_posts
                        else 0
                    )
                )

                like_col, save_col, report_col = st.columns(3)

                with like_col:
                    if st.button(
                        f"♡ {like_count}",
                        key=f"like_{post_id}",
                        use_container_width=True
                    ):
                        if (
                            post_id not in
                            st.session_state.liked_posts
                        ):
                            st.session_state.liked_posts.append(
                                post_id
                            )

                        st.rerun()

                with save_col:
                    if st.button(
                        "🔖 Save",
                        key=f"save_post_{post_id}",
                        use_container_width=True
                    ):
                        if (
                            post_id not in
                            st.session_state.saved_posts
                        ):
                            st.session_state.saved_posts.append(
                                post_id
                            )

                        st.success("Saved.")

                with report_col:
                    if st.button(
                        "⚑ Report",
                        key=f"report_{post_id}",
                        use_container_width=True
                    ):
                        if (
                            post_id not in
                            st.session_state.reported_posts
                        ):
                            st.session_state.reported_posts.append(
                                post_id
                            )

                        st.warning(
                            "Report recorded."
                        )

    with st.expander("🛡️ Community Guidelines"):
        st.markdown("""
- Keep contributions respectful and food-related.
- Do not present personal opinions as medical advice.
- Do not encourage unsafe food-handling practices.
- Respect other participants.
- Harmful or misleading content can be reported.
""")


# ============================================================
# 6. COOKING MODE
# ============================================================

with cooking_tab:

    st.header("👩‍🍳 Cooking Mode")

    recipe = st.session_state.current_recipe

    if not recipe:
        st.info(
            "Choose a meal from My Kitchen first."
        )

    elif not st.session_state.cooking_started:

        st.subheader(
            recipe.get("dish_name", "Your Meal")
        )

        st.write("Ready when you are.")

        if st.button(
            "🔥 Let's Cook",
            type="primary",
            use_container_width=True
        ):
            st.session_state.cooking_started = True
            st.session_state.cooking_step = 0
            st.rerun()

    else:

        steps = recipe.get("steps", [])
        current_step = st.session_state.cooking_step

        if not steps:
            st.warning(
                "No cooking steps were generated."
            )

        elif current_step < len(steps):

            st.caption(
                f"STEP {current_step + 1} OF {len(steps)}"
            )

            st.progress(
                current_step / len(steps)
            )

            st.subheader(
                steps[current_step]
            )

            previous_col, next_col = st.columns(2)

            with previous_col:
                if st.button(
                    "← Previous",
                    disabled=(current_step == 0),
                    use_container_width=True
                ):
                    st.session_state.cooking_step -= 1
                    st.rerun()

            with next_col:

                if current_step == len(steps) - 1:
                    button_text = "Finish Cooking ✓"
                else:
                    button_text = "Done — Next Step →"

                if st.button(
                    button_text,
                    type="primary",
                    use_container_width=True
                ):
                    st.session_state.cooking_step += 1
                    st.rerun()

        else:

            st.progress(1.0)
            st.success("You made it! 🍽️")

            st.header(
                recipe.get("dish_name", "Your Meal")
            )

            rating = st.slider(
                "How did it turn out?",
                min_value=1,
                max_value=5,
                value=4
            )

            make_again = st.radio(
                "Would you make this again?",
                ["Yes", "Maybe", "No"],
                horizontal=True
            )

            leftovers = st.radio(
                "Any leftovers?",
                ["No", "Yes"],
                horizontal=True
            )

            if st.button(
                "🍽️ I Made This",
                type="primary",
                use_container_width=True
            ):

                record = {
                    "dish_name": recipe.get(
                        "dish_name",
                        "Meal"
                    ),
                    "ingredients": recipe.get(
                        "ingredients",
                        []
                    ),
                    "nutrition": recipe.get(
                        "nutrition",
                        {}
                    ),
                    "rating": rating,
                    "make_again": make_again,
                    "leftovers": leftovers
                }

                st.session_state.cooking_history.append(
                    record
                )

                if (
                    recipe not in
                    st.session_state.saved_recipes
                ):
                    st.session_state.saved_recipes.append(
                        recipe
                    )

                st.session_state.cooking_started = False
                st.session_state.cooking_step = 0

                st.success(
                    "Meal logged. Your Kitchen Insights "
                    "have been updated."
                )

                st.info(
                    "Your cooking experience can now become "
                    "community value — open 🤝 Community "
                    "to share your Story."
                )


# ============================================================
# 7. KITCHEN INSIGHTS
# ============================================================

with insights_tab:

    st.header("📊 Kitchen Insights")

    history = st.session_state.cooking_history

    if not history:
        st.info(
            "Your kitchen story starts with your first meal. "
            "Cook something and tap 'I Made This' to begin."
        )

    else:

        pantry_uses = []
        ratings = []
        repeat_meals = 0

        for meal in history:

            ratings.append(
                meal.get("rating", 0)
            )

            if meal.get("make_again") == "Yes":
                repeat_meals += 1

            for ingredient in meal.get(
                "ingredients",
                []
            ):
                if ingredient.get(
                    "already_have",
                    False
                ):
                    pantry_uses.append(
                        ingredient.get(
                            "name",
                            "Ingredient"
                        )
                    )

        avg_rating = (
            sum(ratings) / len(ratings)
            if ratings
            else 0
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Meals Made",
            len(history)
        )

        c2.metric(
            "Pantry Ingredient Uses",
            len(pantry_uses)
        )

        c3.metric(
            "Average Rating",
            f"{avg_rating:.1f}/5"
        )

        c4.metric(
            "Would Make Again",
            repeat_meals
        )

        st.markdown("---")

        st.subheader("🥕 What You've Been Using")

        if pantry_uses:
            unique_ingredients = list(
                dict.fromkeys(pantry_uses)
            )

            st.write(
                " • ".join(unique_ingredients)
            )

        else:
            st.write(
                "No pantry ingredient use logged yet."
            )

        st.subheader("🍲 Your Cooking History")

        for meal in reversed(history):

            with st.expander(
                meal.get("dish_name", "Meal")
            ):
                st.write(
                    f"⭐ **Rating:** "
                    f"{meal.get('rating', '-')}/5"
                )

                st.write(
                    f"♡ **Make again:** "
                    f"{meal.get('make_again', '-')}"
                )

                st.write(
                    f"🥡 **Leftovers:** "
                    f"{meal.get('leftovers', '-')}"
                )

                nutrition = meal.get(
                    "nutrition",
                    {}
                )

                st.write(
                    "**Nutrition snapshot:** "
                    f"{nutrition.get('calories', 'N/A')} calories, "
                    f"{nutrition.get('protein', 'N/A')} protein "
                    "per serving (approx.)"
                )


# ============================================================
# 8. MY LIBRARY
# ============================================================

with library_tab:

    st.header("📚 My Library")

    saved_meals_tab, inspiration_tab, network_tab = st.tabs([
        "Saved Meals",
        "Food Inspiration",
        "My Network"
    ])

    with saved_meals_tab:

        if not st.session_state.saved_recipes:
            st.info(
                "Meals you save will appear here."
            )

        else:
            for saved_recipe in st.session_state.saved_recipes:

                with st.expander(
                    saved_recipe.get(
                        "dish_name",
                        "Saved Meal"
                    )
                ):
                    st.write(
                        saved_recipe.get(
                            "description",
                            ""
                        )
                    )

                    st.markdown("**Ingredients**")

                    for item in saved_recipe.get(
                        "ingredients",
                        []
                    ):
                        st.write(
                            f"• {item.get('name', 'Ingredient')} "
                            f"— {item.get('quantity', '')}"
                        )

                    st.markdown("**How to make it**")

                    for number, step in enumerate(
                        saved_recipe.get("steps", []),
                        start=1
                    ):
                        st.write(
                            f"{number}. {step}"
                        )

    with inspiration_tab:

        st.write(
            "Saw something you'd like to cook later? "
            "Keep the link here."
        )

        inspiration_url = st.text_input(
            "Food inspiration link",
            placeholder="Paste a recipe, reel or video link"
        )

        inspiration_note = st.text_input(
            "Add a note",
            placeholder="Try this for dinner..."
        )

        if st.button("🔖 Save Inspiration"):

            if inspiration_url.strip():

                st.session_state.saved_links.append({
                    "url": inspiration_url.strip(),
                    "note": inspiration_note.strip()
                })

                st.success("Saved.")

            else:
                st.warning(
                    "Paste a link first."
                )

        if st.session_state.saved_links:

            st.markdown("---")

            for item in st.session_state.saved_links:

                st.markdown(
                    f"**{item.get('note') or 'Food idea'}**"
                )

                st.write(
                    item.get("url", "")
                )

    with network_tab:

        st.subheader("🎥 Followed Creators")

        if st.session_state.followed_creators:
            for name in st.session_state.followed_creators:
                st.write(f"✓ {name}")
        else:
            st.write(
                "You aren't following any creators yet."
            )

        st.subheader("🔖 Saved Creators")

        if st.session_state.saved_creators:
            for name in st.session_state.saved_creators:
                st.write(f"• {name}")
        else:
            st.write(
                "No creators saved yet."
            )

        st.subheader("🥗 Consultation Requests")

        if st.session_state.consultation_requests:

            for request in (
                st.session_state.consultation_requests
            ):
                st.write(
                    f"• {request['nutritionist']} "
                    f"— {request['goal']}"
                )

        else:
            st.write(
                "No consultation requests yet."
            )


# ============================================================
# 9. RUCHI PLUS
# ============================================================

with plus_tab:

    st.header("✨ Ruchi Plus")

    st.write(
        "Ruchi's core experience stays accessible. "
        "Ruchi Plus represents a future premium layer for "
        "deeper personalisation and kitchen intelligence."
    )

    free_col, plus_col = st.columns(2)

    with free_col:

        st.subheader("Ruchi Free")

        st.markdown("""
- Ingredient-led meal suggestions
- Three practical meal choices
- Ingredient Intelligence
- Guided Cooking Mode
- Meal tracking
- Kitchen Insights
- Saved meal library
""")

        st.success("Available in the current experience")

    with plus_col:

        st.subheader("Ruchi Plus")

        st.markdown("""
- Deeper personalisation
- Smarter meal planning
- Persistent pantry intelligence
- Richer preference learning
- Advanced kitchen insights
""")

        st.info("Coming Soon")

    st.caption(
        "No payment or subscription processing is included."
    )


# ============================================================
# 10. WHAT'S NEXT
# ============================================================

with future_tab:

    st.header("🌱 Food Donation Drives")

    st.write(
        "Ruchi begins by helping people make better use of "
        "food they already have. Ruchi Story can eventually "
        "extend that principle to usable surplus food."
    )

    st.info("Coming Soon")

    st.markdown("""
### Future journey

**Usable surplus food**

↓

**Verified donation initiatives**

↓

**Safe redistribution**

A real implementation would require participant verification,
food-safety rules, perishability controls, logistics,
accountability and clear responsibility for fulfilment.
""")

    st.markdown("---")

    st.header("How Ruchi Became Ruchi Story")

    st.markdown("""
### Ruchi

**User → Kitchen Intelligence → Meal Decision → Cooking → Learning**

Ruchi creates value **for the individual user**.

### Ruchi Story

**User ↔ Grocery Providers ↔ Creators ↔ Nutritionists ↔ Community**

Ruchi Story enables different participants to create value
**for each other**.

The original Ruchi intelligence layer remains at the centre.
The platform extends the moments in the food journey where
another participant can add value.
""")

    st.markdown("---")

    st.header("Platform Design")

    with st.expander(
        "1. Design for Thickness",
        expanded=True
    ):
        st.write(
            "Ruchi Story brings multiple relevant participants "
            "around the user's food journey — providers, creators, "
            "nutrition professionals and other users."
        )

    with st.expander("2. Avoid Congestion"):
        st.write(
            "Filtering, matching and sorting help users reach "
            "relevant participants instead of browsing an "
            "unstructured marketplace."
        )

    with st.expander(
        "3. Mitigate Asymmetric Information"
    ):
        st.write(
            "Participant profiles expose information such as "
            "speciality, ratings, verification indicators and "
            "fulfilment information."
        )

    with st.expander(
        "4. Ensure Participants' Safety"
    ):
        st.write(
            "Reporting, community guidelines, professional "
            "disclaimers and verification mechanisms form the "
            "starting governance layer."
        )

    with st.expander(
        "5. Align Monetisation with Platform Goals"
    ):
        st.write(
            "Future monetisation can be connected to successful "
            "value exchange, such as completed marketplace "
            "transactions, rather than unrelated advertising."
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Ruchi Story · Make More of What You Have."
)
