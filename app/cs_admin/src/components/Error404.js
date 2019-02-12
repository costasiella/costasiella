// @flow

import * as React from "react";

import { Error404Page } from "tabler-react";

type Props = {||}

function Error404(props: Props): React.Node {
  return <Error404Page />
}

export default Error404

// import { 
//   Container, 
//   Error404Page,
//   Page 
// } from "tabler-react"

// const NotFound = () => {
//   return (
//     <Page>
//       <Container>
//         <Error404Page title="404"
//                       subtitle="Oops... this page couldn't be found"
//                       details="" />
//       </Container>
//     </Page>
//   // <div>
//   //   <h2>Not Found</h2>
//   //   <p>The page you're looking for does not exists.</p>
//   // </div>
//   )
// }

// export default NotFound