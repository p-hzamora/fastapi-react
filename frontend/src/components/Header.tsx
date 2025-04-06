import { Heading, Flex, Separator } from "@chakra-ui/react";

const Header = () => {
  return (
    <Flex>
      <Flex align="center" as="nav" mr={5}>
        <Heading as="h1" size="sm">Login</Heading>
        <Separator />
      </Flex>
    </Flex>
  );
};

export default Header;