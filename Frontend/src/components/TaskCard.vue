<template>
  <div class="task-card">
    <div class="remove-task" @click="removeTask">
      <i class="fas fa-xmark" style="cursor: pointer"></i>
    </div>
    <div class="absolutes">
      <div class="edit-task" @click="editTask">
        <i class="fas fa-edit" style="cursor: pointer"></i>
      </div>
      <div v-show="prevStatus" class="prev-list" @click="prevList">
        <i class="fas fa-circle-chevron-left" style="cursor: pointer"></i>
      </div>
      <div v-show="nextStatus" class="next-list" @click="nextList">
        <i class="fas fa-circle-chevron-right" style="cursor: pointer"></i>
      </div>
    </div>
    <div v-if="task.status === 'done'" class="note">
      <p class="done">DONE</p>
    </div>
    <div v-else class="note">
      <p class="missed" v-if="dateDifference < 0">MISSED</p>
      <p class="urgent" v-if="dateDifference >= 0 && dateDifference <= 3">URGENT</p>
    </div>

    <div class="task">
      <h1 class="task-title">{{ task.title }}</h1>
      <p class="task-description">{{ task.description }}</p>
      <p class="task-date">Deadline: {{ task.due_date }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: "TaskCard",
  data() {
    return {
      dateDifference: null
    }
  },
  props: {
    task: Object,
    nextStatus: String,
    prevStatus: String
  },
  mounted() {
    this.calculateDateDifference();
  },
  methods: {
    async removeTask() {
      try {
        await this.$emit("remove-task");
      } catch (error) {
        console.error("Error removing task:", error);
      }
    },
    nextList() {
        this.$emit("next-list", this.nextStatus, this.task);
    },
    prevList() {
        this.$emit("prev-list", this.prevStatus, this.task);
    },
    editTask() {
      this.$emit("edit-task", this.task);
    },
    calculateDateDifference() {
      const currentDate = new Date();
      const inputDateObject = new Date(this.task.due_date);
      const timeDifference = inputDateObject.getTime() - currentDate.getTime();
      const daysDifference = Math.ceil(timeDifference / (1000 * 60 * 60 * 24));

      this.dateDifference = daysDifference;
    },
  },
};
</script>

<style scoped>
.absolutes {
  display: none;
}
.edit-task {
  bottom: 10px;
  position: absolute;
  left: 10px;
} 
.task-card:hover .absolutes {
  display: block;
}
.prev-list,
.next-list {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
}
.note {
  position: absolute;
  top: 5px;
  left: 0px;
  display: block;
}
.missed {
  background-color: red;
  color: white;
  padding: 3px 5px;
  font-size: 13px;
  font-weight: 600;
  border-top-right-radius: 0.25rem;
  border-bottom-right-radius: 0.25rem;
}
.urgent {
  background-color: orange;
  color: white;
  padding: 3px 5px;
  font-size: 13px;
  font-weight: 600;
  border-top-right-radius: 0.25rem;
  border-bottom-right-radius: 0.25rem;
}
.done {
  background-color: green;
  color: white;
  padding: 3px 5px;
  font-size: 13px;
  font-weight: 600;
  border-top-right-radius: 0.25rem;
  border-bottom-right-radius: 0.25rem;
}

.prev-list {
  left: 15px;
}

.next-list {
  right: 0px;
}
.task-card {
  background-color: #ffffff;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 2px;
  margin: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: relative;
}
.remove-task {
  position: absolute;
  top: 10px;
  right: 10px;
}

.task-card:hover {
  border-color: #0096ff;
  border-radius: 0.5rem;
  box-shadow: 0 5px 10px rgba(0, 0, 0, 0.2);
  border-width: 1.5px;
}

.task-title {
  font-size: 1rem;
}

.task-description {
  font-size: 0.9rem;
}

.task-date {
  color: #888;
  font-size: 0.8rem;
}

.task {
  padding: 0 15px;
}
</style>
