<template>
  <div>
     <!-- Added a separate code here for the custom list since I still want to use the component for adding custom list in my HomeView -->
    <div v-if="custom" class="list">
      <p
        class="custom-list-button"
        v-show="
          !tasks.find((task) => task.status === 'custom') &&
          customListButton &&
          customList === null
        "
        @click="(customListButton = false), (showListForm = !showListForm)"
      >
        + Add a Customized List
      </p>
      <div
        class="task-card"
        style="margin: 0; border: none"
        v-show="showListForm"
      >
        <div class="task">
          <form v-on:submit.prevent="handleAddList">
            <textarea
              class="task-title"
              v-model="customList"
              type="text"
              placeholder="Title..."
            ></textarea>
            <div class="button-container">
              <button
                class="add-task-button"
                type="submit"
                :disabled="this.customList ? false : true"
                @click="(showList = !showList), (showListForm = !showListForm)"
              >
                Add list
              </button>
              <button
                @click="
                  (customListButton = !customListButton),
                    (showListForm = !showListForm)
                "
                type="button"
                class="cancel-button"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
      <div v-show="customList !== null">
        <div class="list-card">
          <h1>{{ customList ? customList.toUpperCase() : customList }}</h1>
          <div class="display-list">
            <div v-for="task in tasks" :key="task.pk">
              <TaskCard
                v-show="task.status === 'custom'"
                :task="task"
                prevStatus="done"
                @remove-task="removeTask(task.pk)"
                @edit-task="editTask"
                @prev-list="prevList"
              />
            </div>
            <div class="task-card" v-show="addTaskButtonCustom">
              <div class="task">
                <form v-on:submit.prevent="addTask">
                  <textarea
                    class="task-title"
                    v-model="title"
                    type="text"
                    placeholder="Title..."
                  ></textarea>
                  <textarea
                    class="task-description"
                    v-model="description"
                    type="text"
                    placeholder="Description..."
                  ></textarea>
                  <input
                    class="task-date"
                    type="date"
                    v-model="due_date"
                    placeholder="Date..."
                  />
                  <div class="button-container">
                    <button
                      class="add-task-button"
                      type="submit"
                      @click="status = 'custom'"
                    >
                      Add card
                    </button>
                    <button
                      @click="addTaskButtonCustom = !addTaskButtonCustom"
                      type="button"
                      class="cancel-button"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            </div>
            <div
              class="remove-container"
              @click="removeList"
              v-show="!tasks.find((task) => task.status === 'custom')"
            >
              <div class="remove">
                <div class="remove-list-button">
                  <i class="fas fa-trash trash-button"></i>
                </div>
                <p>Remove this list</p>
              </div>
            </div>
            <p
              class="add-button"
              @click="addTaskButtonCustom = !addTaskButtonCustom"
            >
              + Create new card
            </p>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="list">
      <div class="list-card">
        <h1>{{ listName.toUpperCase() }}</h1>
        <div class="display-list">
          <div v-for="task in tasks" :key="task.pk">
            <TaskCard
              v-show="task.status === listName"
              :task="task"
              :nextStatus="nextStatus"
              :prevStatus="prevStatus"
              @edit-task="editTask"
              @remove-task="removeTask(task.pk)"
              @next-list="nextList"
              @prev-list="prevList"
            />
          </div>
          <div class="task-card" v-show="addTaskButton">
            <div class="task">
              <form v-on:submit.prevent="addTask">
                <textarea
                  class="task-title"
                  v-model="title"
                  type="text"
                  placeholder="Title..."
                ></textarea>
                <textarea
                  class="task-description"
                  v-model="description"
                  type="text"
                  placeholder="Description..."
                ></textarea>
                <input
                  class="task-date"
                  type="date"
                  v-model="due_date"
                  placeholder="Date..."
                />
                <div class="button-container">
                  <button
                    class="add-task-button"
                    type="submit"
                    @click="(status = listName), (edit = false)"
                  >
                    Add card
                  </button>
                  <button
                    :type="edit === true ? 'submit' : 'button'"
                    @click="handleCancel"
                    class="cancel-button"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
          <p class="add-button" @click="addTaskButton = !addTaskButton">
            + Create new card
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import sileo from "sileo";

const Tasks = new sileo.Model("task", "tasks");
const CustomList = new sileo.Model("custom", "custom-list");

import TaskCard from "@/components/TaskCard.vue";
import Loader from "@/components/Loader.vue";

export default {
  name: "HomeView",
  data() {
    return {
      tasks: [],
      title: "",
      description: "",
      status: "",
      due_date: "",
      addTaskButton: false,
      edit: false,
      addTaskButtonCustom: false,
      customList: null,
      customListButton: true,
      showListForm: false,
      showList: false,
    };
  },
  props: {
    listName: String,
    nextStatus: String,
    prevStatus: String,
    custom: {
      type: Boolean,
      default: false,
    },
  },
  components: {
    TaskCard,
    Loader,
  },
  async created() {
    await this.getTasks();
    await this.getCustomList();
  },
  methods: {
    async getCustomList() {
      await CustomList.objects
        .filter()
        .then((res) => {
          this.customList = res[0].custom_list;
          this.$emit("customListChange", this.customList);
        })
        .catch((e) => {
          console.log(e);
        });
    },
    async removeList() {
      try {
        await CustomList.objects.update(
          { pk: 1 },
          {
            custom_list: "",
          }
        );
        this.getCustomList();
        window.location.reload(); //Need to have a force refresh to display real-time data.
      } catch (error) {
        console.error("Error updating task:", error);
      }
    },
    async handleAddList() {
      // Making sure that customList field is filled.
      if (this.customList) {
        try {
          await CustomList.objects.update(
            { pk: 1 },
            {
              custom_list: this.customList,
            }
          );
        } catch (error) {
          console.error("Error updating task:", error);
        }
      } else {
        alert("Please fill in list title field.");
      }
    },
    async getTasks() {
      await Tasks.objects
        .filter()
        .then((res) => {
          this.tasks = res;
        })
        .catch((e) => {
          console.log(e);
        });
    },
    async addTask() {
      // Making sure that the description, title, and date fields is filled.
      if (this.description && this.title && this.due_date) {
        try {
          await Tasks.objects.create({
            title: this.title,
            description: this.description,
            status: this.status,
            due_date: this.due_date,
          });
          await this.getTasks();
          this.title = "";
          this.description = "";
          this.status = "";
          this.due_date = "";
        } catch (e) {
          console.error(e);
        }
      } else {
        alert(
          "Please fill in title, description, and date fields before adding the task."
        );
      }
    },
    editTask(task) {
      this.edit = true;
      this.title = task.title;
      this.description = task.description;
      this.status = task.status;
      this.due_date = task.due_date;

      this.removeTask(task.pk);

      this.addTaskButton = true;
    },

    async removeTask(taskId) {
      try {
        this.tasks = this.tasks.filter((task) => task.pk !== taskId);
        await Tasks.objects.delete({ pk: taskId });
      } catch (error) {
        console.error("Error removing task:", error);
      }
    },

    // Change the task list by changing the status of the task.
    async prevList(leftStatus, task) {
      try {
        if (task && task.pk) {
          await Tasks.objects.update(
            { pk: task.pk },
            {
              title: task.title,
              description: task.description,
              status: leftStatus,
              due_date: task.due_date,
            }
          );
          window.location.reload(); //Need to have a force refresh to display real-time data.
          await this.getTasks();
        }
      } catch (error) {
        console.error("Error updating task:", error);
      }
    },

    // Change the task list by changing the status of the task.
    async nextList(rightStatus, task) {
      try {
        if (task && task.pk) {
          await Tasks.objects.update(
            { pk: task.pk },
            {
              title: task.title,
              description: task.description,
              status: rightStatus,
              due_date: task.due_date,
            }
          );
          window.location.reload(); //Need to have a force refresh to display real-time data.
          await this.getTasks();
        }
      } catch (error) {
        console.error("Error updating task:", error);
      }
    },
    handleCancel() {
      this.addTaskButton = !this.addTaskButton;

      //Add a setTimeout so that the this.edit will not directly be false when trying to cancel edit.
      setTimeout(() => {
        this.edit = false;
      }, 1000);
    },
  },
};
</script>

<style scoped lang="scss">
@import "./CardList.scss";
</style>