<template>
  <div id="app">
    <h1></h1>
    <router-view/>
  </div>
</template>

<style lang="scss">
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

body {
  background: #2b5876;
  background: -webkit-linear-gradient(to right, #4e4376, #2b5876);
  background: linear-gradient(to right, #4e4376, #2b5876);
}

nav {
  padding: 30px;
  a {
    font-weight: bold;
    color: #2c3e50;

    &.router-link-exact-active {
      color: #42b983;
    }
  }
}
</style>
