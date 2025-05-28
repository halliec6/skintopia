<template>
  <div class="app">
    <nav class="navbar">
      <div class="container">
        <div class="logo">Skintopia</div>
        <div>
          <a
            href="https://github.com/0felicia0/BeautyRecommender/tree/23dcecf19d9582e10f8e184c49504ce1793d7342"
            target="_blank"
            rel="noopener"
            class="nav-link github-link"
          >
            <img src="@/assets/github.png" alt="GitHub" class="github-logo" />
          </a>
        </div>
      </div>
    </nav>

    <main>
      <router-view />
    </main>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  name: "App",
});
</script>

<style lang="scss">
@import "@/assets/styles/variables";
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: "Arial", sans-serif;
  color: $brown-theme;
}

.container {
  width: 90%;
  max-width: 1200px;
  margin: 0 auto;
}

.navbar {
  background-color: $tan-theme;
  padding: 15px 0;
}

.navbar .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 24px;
  font-weight: 600;
  color: $brown-theme;
}

.github-logo {
  width: 24px;
  height: 24px;
}

.github-link {
  display: flex;
  align-items: center;
}
</style>
