<template>
  <v-app>
    <v-container fluid>
      <v-row align="center" justify="center" v-if="currentUser.perm >= 1">
        <v-card width="80vw" class="pa-md-4 mt-5">
          <v-data-table 
            :headers="headers" 
            :items="desserts"
            
            :item-class="setRowStyle"      
            :options.sync="pagination"        
            :footer-props="{ itemsPerPageText: '每頁的資料筆數' }"
          >
            <template v-slot:top>
              <v-toolbar flat>
                <v-toolbar-title>供應商資料</v-toolbar-title>
                <v-divider class="mx-4" inset vertical></v-divider>
                <v-spacer></v-spacer>
                <v-dialog v-model="dialog" max-width="900px">
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn color="primary" dark class="mb-2" v-bind="attrs" v-on="on">
                      新增資料
                    </v-btn>
                  </template>
                  <v-card>
                    <v-card-title>
                      <span class="text-h5">{{ formTitle }}</span>
                    </v-card-title>

                    <v-card-text>
                      <v-container>
                        <v-row>
                          <v-col cols="12" md="3">
                            <v-text-field 
                              label="供應商名稱" 
                              type="text"
                              v-model="editedItem.sup_name" 
                            />
                            <small class="msgErr" v-text="supNameErrMsg"></small>
                          </v-col>

                          <v-col cols="12" md="3">
                            <v-text-field 
                              label="聯絡地址" 
                              type="text"
                              v-model="editedItem.sup_address" 
                            />
                            <!--<small class="msgErr" v-text="supNameErrMsg"></small>-->
                          </v-col>

                          <v-col cols="12" md="3">
                            <v-text-field 
                              label="聯絡人" 
                              type="text"
                              v-model="editedItem.sup_contact" 
                            />
                            <small class="msgErr" v-text="supContactErrMsg"></small>
                          </v-col>

                          <v-col cols="12" md="3">
                            <v-text-field 
                              label="電話" 
                              type="text"
                              v-model="editedItem.sup_phone" 
                            />
                            <small class="msgErr" v-text="supPhoneErrMsg"></small>
                          </v-col>                          
                        </v-row>

                        <v-row>
                          <v-col cols="12">
                            <v-combobox
                              v-model="temp_product"
                              :items="items"
                              chips
                              clearable
                              label="主要產品"
                              multiple                              
                              solo
                            >
                              <template v-slot:selection="{ attrs, item, select, selected }">
                                <v-chip
                                  v-bind="attrs"
                                  :input-value="selected"
                                  close
                                  label
                                  outlined
                                  color="blue"
                                  @click="select"
                                  @click:close="remove(item)"
                                >
                                  {{ item }}
                                </v-chip>
                              </template>
                            </v-combobox>
                          </v-col>
                        </v-row>
                      </v-container>
                    </v-card-text>

                    <v-card-actions>
                      <v-spacer></v-spacer>
                      <v-btn color="blue darken-1" text @click="close">取消</v-btn>
                      <v-btn v-bind:disabled="disbtn" color="blue darken-1" text @click="save">儲存</v-btn>
                    </v-card-actions>
                  </v-card>
                </v-dialog>
                <v-dialog v-model="dialogDelete" max-width="500px">
                  <v-card>
                    <v-card-title class="text-h5">確定刪除這筆資料?</v-card-title>
                    <v-card-actions>
                      <v-spacer></v-spacer>
                      <v-btn color="blue darken-1" text @click="closeDelete">取消</v-btn>
                      <v-btn color="blue darken-1" text @click="deleteItemConfirm">刪除</v-btn>
                      <v-spacer></v-spacer>
                    </v-card-actions>
                  </v-card>
                </v-dialog>
              </v-toolbar>
            </template>

            <template v-slot:item.sup_products="{ item }">
              <v-chip class="ma-2" small v-for="(pt, index) in item.sup_products" :key="index">
                {{ items[pt-1] }}
              </v-chip>
            </template>

            <template v-slot:[`item.actions`]="{ item }">
              <v-icon class="mr-2" @click="editItem(item)" style="color: blue;">
                mdi-pencil
              </v-icon>
              <v-icon @click="deleteItem(item)" style="color: red;">
                mdi-delete
              </v-icon>
            </template>
            <template v-slot:no-data>
              <v-btn color="primary" @click="initialize">Reset</v-btn>
            </template>
          </v-data-table>
        </v-card>
      </v-row>

      <v-row align="center" justify="space-around" v-else>
          <v-dialog 
            v-model="permDialog"
            transition="dialog-bottom-transition"
            max-width="500"
          >
            <v-card>
              <v-toolbar
                color="primary"
                dark
              >錯誤訊息!</v-toolbar>          
              <v-card-text> 
                <div class="text-h4 pa-12">使用這項功能, 請通知管理人員...</div>
              </v-card-text>
              <v-card-actions class="justify-end">
                <v-spacer></v-spacer>
                <v-btn text @click="permCloseFun"> 取消 </v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog>
      </v-row>      
    </v-container>
  </v-app>
</template>

<script>
import axios from 'axios';
import Common from '../../mixin/common.js'

export default {
  name: 'Supplier',

  mixins: [Common],

  mounted() {
    // if back button is pressed
    window.onpopstate = () => {
      console.log("press back button, good bye...");

      const userData = JSON.parse(localStorage.getItem('loginedUser'));
      userData.setting_items_per_page = this.pagination.itemsPerPage;
      localStorage.setItem('loginedUser', JSON.stringify(userData));
    };
  },

  data: () => ({
    currentUser: {},

    //chips: ['Microscan細菌鑑定試劑', '基因檢測試劑', '離心機'],
    /*
    items: ['基因檢測試劑', '核酸萃取試劑', '離心機', 
            'C13檢測試劑', '能力試驗', '教育訓練','抗血清試劑',
            '血液諮詢', 'Microscan細菌鑑定試劑', '台塑生醫EV71-IgM(rapid-tset)'
    ],
    */
    items: [],
    temp_items: [],

    temp_product: [],
    permDialog: false,

    dialog: false,
    dialogDelete: false,
    disbtn: false,
    supIDErrMsg: '',
    supNameErrMsg: '',
    supContactErrMsg: '',
    supPhoneErrMsg: '',

    pagination: {
      //itemsPerPage: 10,   //預設值, rows/per page
      //page: 1,
    },

    //資料表頭
    headers: [
      //{ text: 'ID', sortable: false, value: 'id', width: '10%', align: 'start'},

      //{ text: '代號', sortable: true, value: 'sup_id', width: '20%', align: 'center' },
      { text: '公司名稱', sortable: true, value: 'sup_name', width: '17%', align: 'left' },
      { text: '聯絡地址', sortable: true, value: 'sup_address', width: '220px', align: 'left' },
      { text: '聯絡人', sortable: false, value: 'sup_contact', width: '70px', align: 'left' },
      { text: '電話', sortable: false, value: 'sup_phone', width: '90px', align: 'left' },
      { text: '主要產品', sortable: false, value: 'sup_products', width: '380px', align: 'center' },
      { text: 'Actions', sortable: false, value: 'actions', width: '80px' },
    ],
    desserts: [],
    temp_desserts: [],

    editedIndex: -1,
    editedItem: {
      //id: 0,
      sup_id: '',
      sup_name: '',
      sup_address: '',
      sup_contact: '',
      sup_phone: '',
      sup_products: []
    },
    defaultItem: {
      sup_id: '',
      sup_name: '',
      sup_address: '',
      sup_contact: '',
      sup_phone: '',
      sup_products: []
    },

    load_SingleTable_ok: false,
    load_2thTable_ok: false,
  }),

  computed: {
    formTitle() {
      return this.editedIndex === -1 ? '新增資料' : '編輯資料'
    },
  },

  watch: {

    dialog(val) {
      val || this.close()
    },

    dialogDelete(val) {
      val || this.closeDelete()
    },

    load_SingleTable_ok(val) {
      if (val) {
        this.desserts = Object.assign([], this.temp_desserts);
      }
    },

    load_2thTable_ok(val) {
      if (val) {
        this.items = Object.assign([], this.temp_items);

        this.load_SingleTable_ok=false;
        this.listSuppliers();
      }
    },

    'editedItem.sup_name': function () {
      let isRule = /^([a-zA-Z\u4e00-\u9fa5_.-]+)$/;
      let result = this.editedItem.sup_name.search(isRule);
      let len=this.editedItem.sup_name.length
      result = (len==0)?0:result
      //if (len==0)
      //  result=0
      this.supNameErrMsg = '';
      //console.log("watch:", result, len)
      if (result == -1 || len > 40) {
        this.supNameErrMsg = '資料格式錯誤!';
      } else {
        this.supNameErrMsg = '';
      }
    },

    'editedItem.sup_contact': function () {
      let isRule = /^([a-zA-Z\u4e00-\u9fa5_.-]+)$/;
      let result = this.editedItem.sup_contact.search(isRule);
      let len = this.editedItem.sup_contact.length;      
      result = (len==0)?0:result
      //if (len==0)
      //  result=0
      this.supContactErrMsg = '';
      //console.log("watch:", result, len)
      if (result == -1 || len > 10) {
        this.supContactErrMsg = '資料格式錯誤!';
      } else {
        this.supContactErrMsg = '';
      }
    },

    'editedItem.sup_phone': function () {
      let isRuleInt = /^[0-9]{10}$/;
      let result = this.editedItem.sup_phone.search(isRuleInt);
      //let len = this.editedItem.sup_phone.length;      
      //result = (len<=10)?0:result
      //if (len==0)
      //  result=0
      this.supPhoneErrMsg = '';
      if (result == -1) {
        this.supPhoneErrMsg = '資料格式錯誤!';
      } else {
        this.supPhoneErrMsg = '';
      }
    },
  },

  created() {
    this.currentUser = JSON.parse(localStorage.getItem("loginedUser"));
    if (this.currentUser.perm == 0) {
      this.permDialog=true;
    }

    this.pagination.itemsPerPage=this.currentUser.setting_items_per_page

    this.load_2thTable_ok=false;
    //this.load_SingleTable_ok=false;

    this.initAxios();
    this.listProducts();

    //this.listSuppliers();
    //this.initialize()
  },

  methods: {
    initialize() {
      this.load_2thTable_ok=false;
      this.listProducts();
      //this.load_SingleTable_ok = false;
      //this.listSuppliers();
      /*
      this.desserts = [
        {
          //id: 1,
          sup_name: 'pmcA',
          sup_id: '1234',
          sup_address: '台中市北區',
          sup_contact: '陳大大',
          sup_phone: '0925251234',
          sup_products: [1, 2, 3]
        },
        {
          //id: 1,
          sup_name: 'pmcB',
          sup_id: '3234',
          sup_address: '台北市信義區',
          sup_contact: '王大大',
          sup_phone: '0925251234',
          sup_products: [1, 2, 4, 6, 10]
        }, 
        {
          //id: 1,
          sup_name: 'pmcC',
          sup_id: '2646',
          sup_contact: '張大大',
          sup_address: '台南市西區',
          sup_phone: '0925251234',
          sup_products: [4, 5, 6]
        }, {
          //id: 1,
          sup_name: 'pmcD',
          sup_id: '0978',
          sup_contact: '林大大',
          sup_address: '高雄市旗津區',
          sup_phone: '0925251234',
          sup_products: [7, 8, 9]
        },
      ]
      */
    },

    listProducts() { 
      const path = '/listProducts';
      console.log("listProducts, Axios get data...")
      axios.get(path)
      .then((res) => {
        this.temp_items = res.data.outputs;
        console.log("GET ok, total records:", res.data.outputs.length);        
        this.load_2thTable_ok=true;
      })
      .catch((error) => {
        console.error(error);
        this.load_2thTable_ok=false;
      });
    },

    listSuppliers() { 
      const path = '/listSuppliers';
      console.log("listSuppliers, Axios get data...")
      axios.get(path)
      .then((res) => {
        this.temp_desserts = res.data.outputs;
        console.log("GET ok, total records:", res.data.outputs.length);        
        this.load_SingleTable_ok=true;
      })
      .catch((error) => {
        console.error(error);
        this.load_SingleTable_ok=false;
      });
    },

    setRowStyle(item) {
      return 'style-1';
    },

    editItem(item) {
      //console.log("edit: ", item)
      this.editedIndex = this.desserts.indexOf(item)
      this.editedItem = Object.assign({}, item)

      this.temp_product=[];
      for (var i = 0; i < this.editedItem.sup_products.length; i++) {
        //console.log("list1: ", this.editedItem.sup_products[i]-1);
        //console.log("list2: ", this.items[this.editedItem.sup_products[i]-1]);
        this.temp_product.push(this.items[this.editedItem.sup_products[i]-1]);
      }
      this.dialog = true
    },

    deleteItem(item) {
      this.editedIndex = this.desserts.indexOf(item)
      this.editedItem = Object.assign({}, item)
      this.dialogDelete = true
    },

    deleteItemConfirm() {
      this.desserts.splice(this.editedIndex, 1)
      this.closeDelete()
    },

    close() {
      this.dialog = false
      this.$nextTick(() => {
        this.editedItem = Object.assign({}, this.defaultItem)
        this.editedIndex = -1
      })

      this.temp_product=[];
    },

    closeDelete() {
      this.dialogDelete = false
      this.$nextTick(() => {
        this.editedItem = Object.assign({}, this.defaultItem)
        this.editedIndex = -1
      })
      
      this.temp_product=[];
    },

    save() {
      this.editedItem.sup_products=[];
      let temp_len=this.temp_product.length

      for (var i = 0; i < temp_len; i++) {
        let tt = this.items.findIndex((element)=>{
          return element === this.temp_product[i];
        })
        this.editedItem.sup_products.push(tt+1);
      }

      if (this.editedIndex > -1) {
        Object.assign(this.desserts[this.editedIndex], this.editedItem)
      } else {
        //this.editedItem.id=this.desserts.length+1;
        this.desserts.push(this.editedItem)
      }

      //this.supNameErrMsg= '';
      //this.supContactErrMsg= '';
      //this.supPhoneErrMsg= '';

      this.close()
    },

    remove(item) {      
      this.temp_product.splice(this.temp_product.indexOf(item), 1);
      //this.chips.splice(this.chips.indexOf(item), 1);
      //this.chips = [...this.chips];
      this.temp_product = [...this.temp_product];
    },

    permCloseFun () {
      this.permDialog = false
      console.log("press permission Close Button...");
      this.$router.push('/navbar'); 
    },
  },
}
</script>

<style lang="scss" scoped>
@import url('https://fonts.googleapis.com/css?family=Noto+Sans+TC:400,500&display=swap&subset=chinese-traditional'
);

div.v-toolbar__title {
  margin: 0;
  font-family: "Noto Sans TC", "Microsoft Yahei", "微軟雅黑", sans-serif;
}

/*
th.text-start{
  font-size: 24px;  
}

@mixin name {
  
}
*/
::v-deep .v-data-table-header {
  background-color: #7DA79D;
}

::v-deep .v-data-table-header th {
  font-size: 1em !important;
}

::v-deep .v-data-table-header th:nth-last-child(1) {
  font-size: 0.8em !important;
}

small.msgErr {
  font-size: 80%;
  color: red;  
  top: -20px;
  position: relative;
}

::v-deep .style-1 td {
  padding-left: 8px !important;
  padding-right: 0px !important;    
}

::v-deep .v-data-table > .v-data-table__wrapper > table > thead > tr > th {
  padding-left: 8px !important;
  padding-right: 0px !important;
  text-align: start !important;
}

::v-deep .v-data-table > .v-data-table__wrapper > table > thead > tr > th:nth-last-child(2) {
  text-align: center !important;
}

::v-deep .v-data-table-header th:nth-last-child(1) span {
  color: #1f4788 !important;
}

::v-deep .style-1 td:nth-last-child(2) > span {
  margin-left: 4px !important;
  margin-right: 0px !important; 
  margin-top: 4px !important; 
  margin-bottom: 4px !important; 
  border-style: solid !important;
  border-color: coral !important;   
}

::v-deep .style-1 td:nth-child(2) {
  font-size: 10px !important;
}
::v-deep .style-1 td:nth-child(4) {
  font-size: 10px !important;
}

</style>