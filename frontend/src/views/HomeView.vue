<template>
  <div class="beauty-recommender">
    <section class="hero">
      <div class="container hero-container">
        <div class="hero-content">
          <h1 class="hero-title">SkinTopia</h1>
          <p class="hero-subtitle">
            Welcome to Skintopia, where skincare recommendations meet
            simplicity.
          </p>
        </div>
        <div class="hero-image">
          <img src="@/assets/products.webp" alt="Skincare products" />
        </div>
      </div>
    </section>

    <!-- survey section -->
    <section class="survey-top">
      <div class="container">
        <div class="question-card">
          <h1 class="heading-2">Skincare Quiz</h1>
          <p class="section-text">
            You are 5 minutes away from discovering your next favorite skincare
            product! Simply fill out the four quesitons below, and we will
            provide you with our AI-powered recommendations.
          </p>
        </div>
      </div>
    </section>

    <section class="survey-middle">
      <div class="container">
        <div class="question-card">
          <h2 class="section-title">What is your skin tone?</h2>
          <p class="section-text">
            Please select the option that is the closest to your skin tone.
          </p>
          <div class="tone-grid">
            <div
              v-for="tone in skinTones"
              :key="tone.label"
              class="tone-box"
              :class="{ selected: skinTone === tone.label }"
              :style="{
                backgroundColor: tone.hex,
                border:
                  skinTone === tone.label ? '3px solid #333' : '1px solid #ccc',
              }"
              @click="skinTone = tone.label"
              :title="tone.label"
            >
              <span class="tone-label">{{ tone.label }}</span>
            </div>
          </div>
        </div>
        <div class="question-card">
          <h2 class="section-title">What is your skin type?</h2>
          <p class="section-text">
            If you are not sure, click
            <a
              href="https://www.cerave.com/skin-smarts/skincare-tips-advice/what-skin-type-do-i-have"
              target="_blank"
              class="help-link"
              >here</a
            >
            to learn more.
          </p>
          <div class="skin-type-grid">
            <div
              class="survey-button"
              :class="{ selected: skinType === 'Dry' }"
              @click="skinType = 'Dry'"
            >
              <span class="button-text">Dry</span>
            </div>
            <div
              class="survey-button"
              :class="{ selected: skinType === 'Oily' }"
              @click="skinType = 'Oily'"
            >
              <span class="button-text">Oily</span>
            </div>
            <div
              class="survey-button"
              :class="{ selected: skinType === 'Combination' }"
              @click="skinType = 'Combination'"
            >
              <span class="button-text">Combination</span>
            </div>
            <div
              class="survey-button"
              :class="{ selected: skinType === 'Normal' }"
              @click="skinType = 'Normal'"
            >
              <span class="button-text">Normal</span>
            </div>
          </div>
        </div>
        <div class="question-card">
          <h2 class="section-title">
            Select the desired product type of recommendations
          </h2>
          <p class="section-text">
            Select all that apply. If you are not sure, select all.
          </p>
          <div class="product-grid">
            <div
              class="survey-button"
              v-for="(option, i) in productCategories"
              :key="i"
              :class="{ selected: product_category.includes(option.value) }"
              @click="toggleProductCategory(option.value)"
            >
              <span class="button-text">{{ option.label }}</span>
            </div>
          </div>
        </div>
        <div class="question-card">
          <h2 class="section-title">Product History</h2>
          <p class="section-text">
            To provide the best possible recommendations, please select and rate
            at least three products you have used before. If possible, include a
            mix of those you liked and disliked. You may also add more than
            three products.
          </p>
          <div class="history-list">
            <div
              class="history-item"
              v-for="(product, index) in products"
              :key="index"
            >
              <v-btn
                icon
                size="small"
                variant="text"
                @click="removeProduct(index)"
                aria-label="Remove product"
              >
                <v-icon>mdi-close</v-icon>
              </v-btn>

              <v-autocomplete
                clearable
                label="Please Type in a Product Name"
                :items="productNames"
                v-model="product.product_name"
                variant="underlined"
                :menu-props="{
                  maxWidth: '500px',
                  contentClass: 'autocomplete-menu',
                }"
              />

              <v-rating
                hover
                :length="5"
                :size="28"
                active-color="brown-theme"
                v-model.number="product.rating"
              />
            </div>
          </div>
        </div>
        <div class="form-controls">
          <button class="small-btn" @click="addProduct">+</button>
          <button class="small-btn" @click="submitForm">Submit</button>
        </div>
      </div>
    </section>

    <section class="recommendations" v-if="recommendations.length > 0">
      <div class="container">
        <h1 class="rec-title">Your Recommendations</h1>
        <div class="rec-grid">
          <div
            class="rec-card"
            v-for="(item, index) in recommendations"
            :key="index"
          >
            <div class="rec-image">
              <img
                :src="`https://www.sephora.com/productimages/sku/s${item.sku_id}-main-zoom.jpg`"
                :alt="item.product_name"
                @error="handleImageError"
              />
            </div>
            <div class="rec-content">
              <h3 class="rec-product-name">{{ item.product_name }}</h3>
              <p class="rec-brand">{{ item.brand_name }}</p>
              <p class="rec-details">
                <strong>Rating:</strong>
                {{ item.rating?.toFixed(2) || "N/A" }} |
                <strong>Price:</strong> {{ item.list_price || "N/A" }}
              </p>
            </div>
            <a
              :href="`https://www.sephora.com/product/${item.product_id}`"
              target="_blank"
              class="small-btn"
            >
              View on Sephora
            </a>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, onMounted } from "vue";
import axios from "axios";

export default defineComponent({
  name: "HomeView",
  setup() {
    const products = reactive([
      { product_name: null, rating: 0 },
      { product_name: null, rating: 0 },
      { product_name: null, rating: 0 },
    ]);

    const responseText = ref("");
    const productNames = ref([]);
    const skinTone = ref("");
    const skinType = ref("");
    const product_category = ref<string[]>([]);
    const recommendations = ref([]);
    const skinTones = [
      { label: "Fair Light", hex: "#ead2b5" },
      { label: "Fair", hex: "#f1bf8b" },
      { label: "Light", hex: "#deae7a" },
      { label: "Light Medium", hex: "#e0a77c" },
      { label: "Medium", hex: "#cc9460" },
      { label: "Medium Tan", hex: "#ca8b5c" },
      { label: "Tan", hex: "#b67f54" },
      { label: "Deep", hex: "#8b5d39" },
      { label: "Rich", hex: "#6d4d30" },
    ];

    const productCategories = [
      { label: "Moisturizers", value: "moisturizers" },
      { label: "Sunscreen", value: "sunscreen" },
      { label: "Toners", value: "toners" },
      { label: "Essence", value: "essense" },
      { label: "Face Masks", value: "face_mask" },
      { label: "Cleansers", value: "cleansers" },
      { label: "Face Serums", value: "face_serums" },
    ];

    const fetchProductNames = async () => {
      try {
        const response = await axios.get("https://skintopia-test.onrender.com/get-products");
        productNames.value = response.data.product_names;
      } catch (error) {
        console.error("Error fetching product names:", error);
      }
    };

    const addProduct = () => {
      products.push({ product_name: null, rating: 0 });
    };

    const removeProduct = (index: number) => {
      if (products.length > 1) {
        products.splice(index, 1);
      }
    };

    const toggleProductCategory = (value: string) => {
      const index = product_category.value.indexOf(value);
      if (index > -1) {
        product_category.value.splice(index, 1);
      } else {
        product_category.value.push(value);
      }
    };

    const handleImageError = (event: any) => {
      event.target.src = "/api/placeholder/120/150";
    };

    const submitForm = async () => {
      try {
        const payload = {
          user_id: "dummy_id", //temp known id
          ratings: products.map((p) => ({
            product_name: p.product_name,
            rating: p.rating,
          })),
          skin_tone: skinTone.value,
          skin_type: skinType.value,
          product_category: product_category.value,
        };

        console.log("PAYLOAD:", payload);

        const response = await axios.post(
          "https://skintopia-test.onrender.com/recommend_lightfm",
          payload
        );
        console.log("RESPONSE", response.data);
        recommendations.value = response.data;
        responseText.value = JSON.stringify(response.data, null, 2);
      } catch (error) {
        console.error("Error:", error);
        responseText.value = "Failed to get recommendations.";
      }
    };

    onMounted(() => {
      fetchProductNames();
    });

    return {
      products,
      productNames,
      addProduct,
      removeProduct,
      toggleProductCategory,
      handleImageError,
      submitForm,
      responseText,
      skinTone,
      skinType,
      product_category,
      recommendations,
      skinTones,
      productCategories,
    };
  },
});
</script>

<style scoped lang="scss">
@import "@/assets/styles/variables";

.hero {
  background-color: $beige-theme;
  padding: 60px 0;
  min-height: 400px;
}

.hero-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.hero-content {
  flex: 1;
  padding-right: 40px;
}

.hero-title {
  font-size: 60px;
  font-weight: 700;
  margin-bottom: 15px;
  color: $brown-theme;
}

.heading-2 {
  font-size: 36px;
  font-weight: 600;
  color: $brown-theme;
}
.hero-subtitle {
  font-size: 18px;
  margin-bottom: 30px;
  line-height: 1.5;
  color: $brown-theme;
}

.hero-image {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.hero-image img {
  max-width: 100%;
  border-radius: 50%;
}

.question-card {
  background-color: $beige-theme;
  padding: 30px;
  border-radius: 8px;
  margin-bottom: 40px;
}

.section-title {
  font-size: 32px;
  color: $brown-theme;
  font-weight: 600;
}

.section-text {
  font-size: 24;
  color: $brown-theme;
  font-weight: 300;
  margin-bottom: 10px;
}

.survey-top {
  background-color: #bcdade;
  padding: 60px 0 20px 0;
}

.tone-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 15px;
}

.tone-box {
  height: 40px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: all 0.3s ease;
}

.tone-box.neutral {
  background-color: #fff;
  border: 1px solid $brown-theme;
}

.tone-box.selected {
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.tone-label {
  background-color: rgba(255, 255, 255, 0.8);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  color: #333;
}

.survey-middle {
  background-color: $blue-theme;
  padding: 0 0 40px 0;
}

.skin-type-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
}

.survey-button {
  height: 60px;
  background-color: $green-theme;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.survey-button:hover {
  background-color: $button-hover;
}

.survey-button.selected {
  background-color: $brown-theme;
  color: white;
  border-color: $brown-theme;
}

.button-text {
  font-weight: 500;
  font-size: 18px;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(3, 1fr);
  gap: 15px;
}

.help-link {
  color: $tan-theme;
}
.history-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.history-item {
  background-color: $green-theme;
  border-radius: 4px;
  padding: 15px;
  position: relative;
}

.form-controls {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
}

.small-btn:hover {
  background-color: $tan-hover;
}

.recommendations {
  background-color: $tan-theme;
  padding: 50px 0;
}

.rec-title {
  font-size: 60px;
  color: $brown-theme;
  margin-bottom: 40px;
  text-align: center;
}

.rec-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 30px;
}

.rec-card {
  border-radius: 8px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: $beige-theme;
}

.rec-image {
  width: 120px;
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 15px;
  border-radius: 4px;
}

.rec-image img {
  max-width: 100%;
  max-height: 100%;
  object-fit: cover;
  border-radius: 4px;
}

.rec-content {
  text-align: center;
  margin-bottom: 15px;
}

.rec-product-name {
  font-size: 16px;
  font-weight: 600;
  color: $brown-theme;
  margin-bottom: 5px;
}

.rec-brand {
  font-size: 14px;
  color: $brown-theme;
  margin-bottom: 8px;
}

.rec-details {
  font-size: 12px;
  color: $brown-theme;
}

.small-btn {
  background-color: $tan-theme;
  border: none;
  color: white;
  padding: 10px 24px;
  border-radius: 20px;
  font-size: 20px;
  cursor: pointer;
  text-decoration: none;
  transition: background-color 0.3s ease;
}

@media (max-width: 768px) {
  .hero-container {
    flex-direction: column;
    text-align: center;
  }

  .hero-content {
    padding-right: 0;
    margin-bottom: 40px;
  }

  .tone-grid,
  .skin-type-grid,
  .product-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .rec-grid {
    grid-template-columns: 1fr;
  }
}
</style>
