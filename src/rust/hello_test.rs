use muluop_rust::get_greeting;

#[test]
fn test_greeting() {
    assert_eq!(get_greeting(), "Hello, World!");
}
