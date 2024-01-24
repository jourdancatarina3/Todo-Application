<template>
  <div class="loader">
    <div class="container">
      <div class="contents">
        <div>
          <h1>asd</h1>
          <p>asd</p>
        </div>
        <div class="list-card">
          <div class="list">
            <div class="card-container">
                <h1 class="list-title">asd</h1>
                <div class="card"></div>
                <div class="card"></div>
                <div class="card"></div>
            </div>
          </div>
          <div class="list">
            <div class="card-container">
                <h1 class="list-title">asd</h1>
                <div class="card"></div>
                <div class="card"></div>
                <div class="card"></div>
            </div>
          </div>
          <div class="list">
            <div class="card-container">
                <h1 class="list-title">asd</h1>
                <div class="card"></div>
                <div class="card"></div>
                <div class="card"></div>
            </div>
          </div>
          <div class="list">
            <div class="card-container">
                <h1 class="list-title">asd</h1>
                <div class="card"></div>
                <div class="card"></div>
                <div class="card"></div>
            </div>
          </div>
          
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Loader",
};
</script>

<style lang="scss" scoped>
@keyframes pulse {
  0%, 100% {
    opacity: 0.6;
  }
  50% {
    opacity: 0.8;
  }
}
.contents {
  padding: 20px;
}
.loader {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #d0d3d8; /* Semi-transparent white background */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999; /* Ensure the loader is above other content */
}
.container {
  width: 1400px;
  height: 724px;
  background-color: white;
  border-radius: 0.75rem;
  border: solid 2px;
  border-color: #f0f0f0;
  box-shadow: 10px 20px 25px -5px rgb(0 0 0 / 0.1),
    0 8px 10px -6px rgb(0 0 0 / 0.1);
}
.list-card {
  display: flex;
  justify-content: start;
}
.list {
  display: flex;
  justify-content: center;
  width: 20rem;
  height: 33rem;
  border: solid 1px;
  border-radius: 0.75rem;
  border-color: lightgrey;
  margin-right: 20px;
}
h1 {
  color: #b0b6bc;
  background-color: #b0b6bc;
  border-radius: 0.75rem;
  width: 20rem;
  padding: 7px;
  animation: pulse 1.5s infinite;
}
p {
  color: #b0b6bc;
  background-color: #b0b6bc;
  border-radius: 0.75rem;
  width: 30rem;
  padding: 7px;
  animation: pulse 1.5s infinite;
}
.list-title {
  color: #b0b6bc;
  background-color: #b0b6bc;
  border-radius: 0.75rem;
  width: 13rem;
  padding: 7px;
  margin: auto;
  animation: pulse 1.5s infinite;
}
.card-container {
    padding: 20px;
    animation: pulse 1.5s infinite;
}
.card {
  width: 18rem;
  margin: 15px 0;
  background-color: #b0b6bc;
  height: 8rem;
  border-radius: 0.75rem;
  animation: pulse 1.5s infinite;
}
</style>