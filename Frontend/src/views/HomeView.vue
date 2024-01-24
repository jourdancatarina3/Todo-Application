<template>
  <div class="home">
    <div class="main-container">
      <div class="list-containers">
        <div class="main">
          <div class="catchphrase">
            <h1>Your List of Tasks</h1>
            <p>Unleash Productivity with Your Personal Task Wizard!</p>
          </div>
          <div class="cardContainers">
            <CardList listName="todo" nextStatus="doing" />
            <CardList listName="doing" nextStatus="done" prevStatus="todo" />
            <CardList
              listName="done"
              :nextStatus="customListNextStatus"
              prevStatus="doing"
              @customListChange="handleCustomListChange"
            />
            <CardList listName="custom" prevStatus="done" :custom="true" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import TaskCard from "@/components/TaskCard.vue";
import CardList from "@/components/CardList.vue";

export default {
  name: "HomeView",
  data() {
    return {
      customList: "",
    };
  },
  computed: {
    customListNextStatus() {
      return this.customList !== null ? "custom" : "";
    },
  },
  methods: {
    handleCustomListChange(newCustomList) {
      this.customList = newCustomList;
      console.log(this.customList);
    },
  },
  components: {
    TaskCard,
    CardList,
  },
};
</script>

<style scoped lang="scss">
@import "./HomeView.scss";
</style>
