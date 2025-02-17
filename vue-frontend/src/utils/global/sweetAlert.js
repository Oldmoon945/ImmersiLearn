import Swal from "sweetalert2";

export const sweetAlert = {
    methods: {
         /**
         * sweetAlert
         * @title 標題
         * @state 狀態 (success, error, warning)
         * @position 顯示位置 (預設 : 中間)
         */
        sweetAlert(title, state, position = 'center') {
            return Swal.fire({
                position: position,
                icon: state,
                title: title,
                showConfirmButton: false,
                timer: 1500,
                timerProgressBar: true
            });
        }
    }
}