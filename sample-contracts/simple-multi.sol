contract A {
    uint32 number;
    address b_addr;

    function set_both(uint32 num) {
        B b = B(b_addr);
        number = num;
        b.set(num);
    }
}

contract B {
    uint32 number;

    function set(uint32 num) {
        number = num;
    }
}

